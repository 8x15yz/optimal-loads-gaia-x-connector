"""JWT/VC consistency and supported signed status-list validation."""
import base64
import gzip
import io
import math
import re
from datetime import datetime,timezone
import httpx
from verification_support import result, certificate_checks

VC_CONTEXT='https://www.w3.org/ns/credentials/v2'
LEGACY={'did:web:registrationnumber.notary.lab.gaia-x.eu:v2','did:web:compliance.lab.gaia-x.eu:development'}

def is_iri(value):
    return isinstance(value,str) and bool(re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s]+',value))

def header_check(h,p,typ):
    pair=('vp+jwt','vp') if typ=='VerifiablePresentation' else ('vc+jwt','vc')
    pairs={pair}
    if typ=='gx:LeiCode' and p.get('issuer')=='did:web:registrationnumber.notary.lab.gaia-x.eu:v2': pairs.add(('vc+ld+jwt','vc+ld'))
    ok=(h.get('iss')==p.get('issuer') and isinstance(p.get('issuer'),str) and
        (h.get('typ'),h.get('cty')) in pairs and h.get('alg') in ('RS256','PS256') and
        isinstance(h.get('kid'),str) and 'crit' not in h and h.get('b64',True) is True and 'zip' not in h and
        'vc' not in p and 'vp' not in p)
    return result('jwt_header','JWT 헤더 일관성','pass' if ok else 'fail','iss ↔ issuer, typ/cty 조합, 허용 알고리즘·헤더 확장 검사')

def time_checks(h,p,now,require_end=True):
    from credentials import date_value
    rows,ends=[],[]
    try:
        start=date_value(p.get('validFrom'))
        end=date_value(p['validUntil']) if 'validUntil' in p else None
        ok=start<=now and (end is not None or not require_end) and (end is None or start<end and now<end)
        if end: ends.append(end)
        rows.append(result('vc_time','VC 유효기간','pass' if ok else 'fail',f"{p.get('validFrom')} ~ {p.get('validUntil','미지정')}"))
    except (ValueError,TypeError,OverflowError):
        rows.append(result('vc_time','VC 유효기간','fail','시간대가 있는 RFC3339 validFrom / validUntil 필요'))
    values={}
    try:
        for name in ('exp','nbf','iat'):
            if name not in p: continue
            val=p[name]
            if isinstance(val,bool) or not isinstance(val,(float,int)) or not math.isfinite(val): raise ValueError('NumericDate 형식 오류')
            values[name]=datetime.fromtimestamp(val,timezone.utc)
        if values:
            ok=('exp' not in values or now<values['exp']) and ('nbf' not in values or values['nbf']<=now) and ('iat' not in values or values['iat'].timestamp()<=now.timestamp()+60)
            if 'exp' in values:
                ends.append(values['exp'])
                ok=ok and all(values[t]<values['exp'] for t in ('iat','nbf') if t in values)
            rows.append(result('jwt_time','JWT NumericDate','pass' if ok else 'fail','본문 exp/nbf/iat를 초 단위로 독립 검사'))
        else: rows.append(result('jwt_time','JWT NumericDate','not_applicable','본문 exp/nbf/iat 없음; VC 유효기간으로 제한',False))
    except (ValueError,TypeError,OverflowError,OSError):
        rows.append(result('jwt_time','JWT NumericDate','fail','NumericDate 형식·범위 오류 (밀리초를 초로 허용하지 않음)'))
    if 'iat' in h or 'exp' in h:
        try:
            if p.get('issuer') not in LEGACY or not all(type(h.get(k)) is int for k in ('iat','exp')): raise ValueError()
            a,b=(datetime.fromtimestamp(h[k]/1000,timezone.utc) for k in ('iat','exp'))
            ok=a<=now<b and abs((a-date_value(p['validFrom'])).total_seconds())<2 and abs((b-date_value(p['validUntil'])).total_seconds())<2
            ends.append(b)
            rows.append(result('legacy_time','Loire 헤더 시간','pass' if ok else 'fail','알려진 Lab 발급자 밀리초 확장과 VC 날짜 대조; 표준 본문 NumericDate와 별개'))
        except (ValueError,TypeError,KeyError,OverflowError,OSError):
            rows.append(result('legacy_time','Loire 헤더 시간','fail','허용하지 않는 헤더 시간 형식'))
    return rows,ends

def status_checks(p,doc,policy,now,fetcher,cache):
    from credentials import unpack,signature
    if 'credentialStatus' not in p:
        return [result('vc_status','VC 폐기·정지','unknown','credentialStatus 없음: 폐기되지 않았음을 증명하지 못함',False)],[]
    entries=p['credentialStatus']
    entries=entries if isinstance(entries,list) else [entries]
    if not 1<=len(entries)<=4: return [result('vc_status','VC 폐기·정지','fail','status 항목은 1~4개 필요')],[]
    rows,ends=[],[]
    for entry in entries:
        try:
            if not isinstance(entry,dict) or not is_iri(entry.get('id')): raise ValueError('status id 형식 오류')
            if entry.get('type')!='BitstringStatusListEntry' or entry.get('statusPurpose') not in ('revocation','suspension'):
                rows.append(result('vc_status','VC 폐기·정지','unknown','미지원 status 유형 또는 목적; 데모 연결 차단')); continue
            idx=entry.get('statusListIndex')
            if not isinstance(idx,str) or not re.fullmatch(r'0|[1-9][0-9]{0,8}',idx): raise ValueError('statusListIndex 형식 오류')
            idx=int(idx); url=entry.get('statusListCredential'); issuer=p.get('issuer')
            if not isinstance(url,str) or policy.get('status_list_urls',{}).get(url)!=issuer:
                rows.append(result('vc_status','VC 폐기·정지','unknown','관리자가 신뢰 URL·발급자를 등록하지 않은 status list')); continue
            if url not in cache: cache[url]=fetcher(url,policy['status_list_urls'],512_000)
            token=cache[url].decode('utf-8').strip()
            if token.startswith('{'):
                from credentials import strict_json
                wrapped=strict_json(token)
                if wrapped.get('type')!='EnvelopedVerifiableCredential' or not wrapped.get('id','').startswith('data:application/vc+jwt,'): raise ValueError('상태 목록 envelope 미지원')
                token=wrapped['id'].split(',',1)[1]
            h,sp=unpack(token)
            types=sp.get('type',[]); context=sp.get('@context',[])
            if not isinstance(types,list) or not {'VerifiableCredential','BitstringStatusListCredential'}<=set(types): raise ValueError('상태 목록 VC type 오류')
            if context != [VC_CONTEXT]: raise ValueError('상태 목록은 고정된 W3C VC v2 context만 지원')
            if sp.get('issuer')!=issuer or sp.get('id')!=url: raise ValueError('상태 목록 발급자·ID 불일치')
            if header_check(h,sp,'BitstringStatusListCredential')['status']!='pass': raise ValueError('상태 목록 헤더 오류')
            sig,detail=signature(h,sp,token,doc)
            if sig!='pass': raise ValueError('상태 목록 '+detail)
            method=next(m for m in doc['verificationMethod'] if m.get('id')==h['kid'])
            certrows,certend=certificate_checks(method,issuer,policy,now,fetcher)
            if any(r['required_for_demo'] and r['status']!='pass' for r in certrows): raise ValueError('상태 목록 서명 인증서 검증 실패')
            if certend: ends.append(certend)
            tr,te=time_checks(h,sp,now,require_end=False); ends.extend(te)
            if any(r['required_for_demo'] and r['status']!='pass' for r in tr): raise ValueError('상태 목록 기간 오류')
            if 'credentialStatus' in sp:
                rows.append(result('vc_status','VC 폐기·정지','unknown','재귀 상태 목록 조회 미지원')); continue
            sub=sp.get('credentialSubject',{})
            if not isinstance(sub,dict) or not is_iri(sub.get('id')) or sub.get('type')!='BitstringStatusList' or sub.get('statusPurpose')!=entry['statusPurpose']: raise ValueError('상태 목록 subject·purpose 오류')
            if type(sub.get('statusSize',1)) is not int or sub.get('statusSize',1)!=1: raise ValueError('1-bit 상태 목록만 지원')
            encoded=sub.get('encodedList','')
            if not isinstance(encoded,str) or not re.fullmatch(r'u[A-Za-z0-9_-]+',encoded): raise ValueError('multibase base64url encodedList 필요')
            raw=base64.urlsafe_b64decode(encoded[1:]+'='*(-len(encoded[1:])%4))
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as g: bits=g.read(1_048_577)
            if not 16_384<=len(bits)<=1_048_576 or idx>=len(bits)*8: raise ValueError('상태 목록 크기·index 범위 오류')
            active=bool(bits[idx//8] & (1<<(7-idx%8)))
            rows.append(result('vc_status','VC 폐기·정지','fail' if active else 'pass',f"서명된 {entry['statusPurpose']} 목록: index {idx} = {int(active)}"))
        except (httpx.HTTPError,OSError) as e:
            rows.append(result('vc_status','VC 폐기·정지','unknown','상태 목록 조회/압축 처리 불가: '+type(e).__name__))
        except Exception as e:
            rows.append(result('vc_status','VC 폐기·정지','fail',str(e)[:220]))
    return rows,ends
