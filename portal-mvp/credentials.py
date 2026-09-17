"""Loire demo import profile. Decoding, cryptographic checks and trust are separate."""
import base64
import hashlib
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

import httpx
import jwt
import rfc8785
from cryptography.hazmat.primitives.asymmetric import rsa
from verification_support import load_policy, remote_bytes, result, certificate_checks
from schema_validation import schema_check
from credential_checks import is_iri, header_check, time_checks, status_checks

MAX_FILE = 2_000_000
MAX_TOTAL = 8_000_000
PROFILE = 'loire-demo-v2'
TRUSTED = {
    'did:web:vc-jwt.io': {'gx:LegalPerson', 'gx:Issuer', 'VerifiablePresentation'},
    'did:web:registrationnumber.notary.lab.gaia-x.eu:v2': {'gx:LeiCode'},
    'did:web:compliance.lab.gaia-x.eu:development': {'gx:LabelCredential'},
}
REQUIRED = {'gx:LegalPerson', 'gx:Issuer', 'gx:LeiCode', 'gx:LabelCredential'}

def strict_json(data):
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError('중복 JSON 키: ' + k)
            obj[k] = v
        return obj
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('유효하지 않은 JSON 숫자')))

def unpack(token):
    if not isinstance(token, str) or len(token) > MAX_FILE:
        raise ValueError('JWT 크기 또는 형식 오류')
    parts = token.strip().split('.')
    if len(parts) != 3 or any(not re.fullmatch(r'[A-Za-z0-9_-]+', p) for p in parts):
        raise ValueError('서명된 compact JWT 형식이 필요합니다')
    objs = [strict_json(base64.urlsafe_b64decode(x + '=' * (-len(x) % 4))) for x in parts[:2]]
    if not all(isinstance(x, dict) for x in objs):
        raise ValueError('JWT 헤더·본문은 JSON 객체여야 합니다')
    return objs

def kind(payload):
    types = payload.get('type', [])
    if isinstance(types, str):
        types = [types]
    if not isinstance(types, list) or not all(isinstance(x, str) for x in types):
        raise ValueError('type 형식 오류')
    matches = [x for x in types if x in REQUIRED]
    if len(matches)>1 or len(types)!=len(set(types)):
        raise ValueError('중복 또는 복수 자격증명 유형')
    if 'VerifiablePresentation' in types:
        if matches or 'VerifiableCredential' in types: raise ValueError('VC/VP 유형 혼합')
        return 'VerifiablePresentation'
    return matches[0] if matches else 'Unknown'

def read_uploads(files):
    """No ZIP extraction onto disk; cap members, size and supported extension."""
    found = []
    total = 0
    for name, data in files:
        total += len(data)
        if total > MAX_TOTAL:
            raise ValueError('전체 업로드는 8 MB 이하여야 합니다')
        if name.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if len(z.infolist()) > 20:
                    raise ValueError('ZIP 파일 항목은 20개 이하여야 합니다')
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    if not info.filename.lower().endswith('.jwt'):
                        raise ValueError('ZIP에는 .jwt 파일만 넣어주세요')
                    if info.file_size > MAX_FILE:
                        raise ValueError('개별 JWT는 2 MB 이하여야 합니다')
                    total += info.file_size
                    if total > MAX_TOTAL:
                        raise ValueError('압축 해제 크기 제한 초과')
                    found.append((info.filename, z.read(info).decode('utf-8-sig').strip()))
        elif name.lower().endswith('.jwt') and len(data) <= MAX_FILE:
            found.append((name, data.decode('utf-8-sig').strip()))
        else:
            raise ValueError('.jwt 또는 .zip 파일을 선택해주세요')
    if not found or len(found) > 20:
        raise ValueError('JWT 파일 1~20개가 필요합니다')
    return found

def did_url(did):
    # Only known demo issuers are remotely fetched. No arbitrary user URL fetching.
    if did not in TRUSTED:
        raise ValueError('허용된 데모 발급자 DID가 아닙니다')
    parts = did[len('did:web:'):].split(':')
    host = unquote(parts[0])
    suffix = '/'.join(parts[1:])
    return f'https://{host}/' + (suffix + '/did.json' if suffix else '.well-known/did.json')

def fetch_document(did):
    url = did_url(did)
    data = remote_bytes(url, [url], 256_000)
    doc = strict_json(data)
    if not isinstance(doc, dict) or doc.get('id') != did:
        raise ValueError('DID 문서 id 불일치')
    return doc

def signature(header, payload, token, doc):
    if isinstance(doc, Exception):
        return 'unknown', '공개키 조회 실패: ' + type(doc).__name__
    if doc is None:
        return 'unknown', '허용 발급자의 공개키를 찾을 수 없음'
    issuer = payload.get('issuer')
    if not isinstance(doc,dict) or doc.get('id') != issuer:
        return 'fail', 'DID 문서 id와 발급자 불일치'
    kid = header.get('kid', '')
    if not isinstance(kid, str) or not kid.startswith(str(issuer) + '#'):
        return 'fail', 'kid와 issuer 관계 불일치'
    methods = doc.get('verificationMethod', [])
    if not isinstance(methods,list) or not all(isinstance(m,dict) for m in methods):
        return 'fail', 'verificationMethod 형식 오류'
    matches = [m for m in methods if m.get('id') == kid]
    method = matches[0] if len(matches)==1 else None
    if not method or method.get('controller') != issuer:
        return 'fail', '검증 키 또는 controller 불일치'
    purposes = doc.get('assertionMethod', [])
    if not isinstance(purposes,list): return 'fail', 'assertionMethod 형식 오류'
    if kid not in [m.get('id') if isinstance(m, dict) else m for m in purposes]:
        return 'fail', 'assertionMethod로 허용되지 않은 키'
    if header.get('alg') not in {'RS256', 'PS256'}:
        return 'fail', '이 가져오기 프로필에서 허용하지 않는 알고리즘'
    try:
        jwk = method['publicKeyJwk']
        if jwk.get('kty')!='RSA' or any(k in jwk for k in ('d','p','q','dp','dq','qi','oth')):
            raise ValueError('공개 RSA JWK 필요')
        if jwk.get('alg',header['alg'])!=header['alg'] or jwk.get('use','sig')!='sig':
            raise ValueError('JWK 용도·알고리즘 불일치')
        if 'key_ops' in jwk and (not isinstance(jwk['key_ops'],list) or 'verify' not in jwk['key_ops']):
            raise ValueError('JWK 검증 용도 불허')
        key = jwt.PyJWK.from_dict(jwk, algorithm=header['alg']).key
        if not isinstance(key,rsa.RSAPublicKey) or key.key_size<2048: raise ValueError('RSA 2048 bit 이상 필요')
        # Deliberately only cryptographic validation here. VC dates checked separately.
        jwt.decode(token, key, algorithms=[header['alg']], options={
            'verify_exp': False, 'verify_iat': False, 'verify_nbf': False,
            'verify_aud': False, 'verify_iss': False, 'verify_sub': False,
            'verify_jti': False})
        return 'pass', '공개키로 원본 JWT 서명 검증 성공'
    except Exception as e:
        return 'fail', '서명 검증 실패: ' + type(e).__name__

def date_value(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',value):
        raise ValueError('시간대가 있는 RFC3339 시간 필요')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('시간대 필요')
    return dt

CRITERIA_BASE = 'https://docs.gaia-x.eu/policy-rules-committee/compliance-document/'

def compliance_profile(policy):
    """Compliance VC 수용 기준. Lab 발급 형식·규칙 버전이 자주 바뀌어 버전 문자열은 필수 판정에 쓰지 않음.

    구 정책 파일(accepted_profiles 또는 required_criteria만 있음)도 그대로 동작하도록 변환.
    """
    prof = policy.get('compliance_profile')
    if isinstance(prof, dict):
        return {'label_levels': prof.get('label_levels', ['SC']),
                'known_rules_versions': prof.get('known_rules_versions', []),
                'required_criteria_suffixes': prof.get('required_criteria_suffixes', ['criteria_participant/#PA1.1'])}
    legacy = policy.get('accepted_profiles') or {'CD25.10': {'label_levels': ['SC'], 'required_criteria': policy.get('required_criteria', [])}}
    levels = sorted({l for v in legacy.values() for l in v.get('label_levels', [])}) or ['SC']
    suffixes = sorted({c.split('/compliance-document/', 1)[-1].split('/', 1)[-1] for v in legacy.values() for c in v.get('required_criteria', [])})
    return {'label_levels': levels, 'known_rules_versions': list(legacy), 'required_criteria_suffixes': suffixes or ['criteria_participant/#PA1.1']}

def ref_credential_type(ref):
    """참조 유형 키 변천: type(09/08) → gx:credentialType(09/16~). 접두사 없는 표기도 수용."""
    value = ref.get('gx:credentialType') or ref.get('credentialType') or ref.get('type')
    if isinstance(value, list):
        value = next((v for v in value if isinstance(v, str) and v.removeprefix('gx:') in {t.removeprefix('gx:') for t in REQUIRED}), None)
    if isinstance(value, str) and not value.startswith('gx:') and ':' not in value:
        value = 'gx:' + value
    return value

def ref_digest(ref):
    """해시 키 변천: gx:digestSRI(~09/16) → digestSRI(W3C VC v2, 09/17~)."""
    return ref.get('gx:digestSRI') or ref.get('digestSRI')

def inspect_set(named_tokens, resolver=fetch_document, *, resource_fetcher=remote_bytes, policy=None, now=None):
    policy = load_policy() if policy is None else policy
    if policy.get('profile')!=PROFILE: raise ValueError('검증 정책 프로필 불일치')
    docs, by_id, by_token = [], {}, set()
    def add(name, token, depth=0):
        if token in by_token:
            return
        if len(docs) >= 20 or depth > 1:
            raise ValueError('중첩 또는 자격증명 개수 제한 초과')
        header, payload = unpack(token)
        typ = kind(payload)
        ident = payload.get('id')
        if ident and not isinstance(ident, str):
            raise ValueError('id는 문자열이어야 합니다')
        if ident in by_id and by_id[ident] != token:
            raise ValueError('동일 ID에 서로 다른 JWT가 제출되었습니다: ' + ident)
        if ident:
            by_id[ident] = token
        by_token.add(token)
        docs.append({'file': name, 'header': header, 'payload': payload, 'token': token, 'kind': typ})
        if typ == 'VerifiablePresentation':
            if depth:
                raise ValueError('중첩 VP는 지원하지 않습니다')
            vcs = payload.get('verifiableCredential')
            if not isinstance(vcs, list) or not 1 <= len(vcs) <= 10:
                raise ValueError('VP의 VC 배열이 필요합니다')
            for i, item in enumerate(vcs):
                if not isinstance(item, dict) or item.get('type') != 'EnvelopedVerifiableCredential':
                    raise ValueError('EnvelopedVerifiableCredential 형식을 지원합니다')
                data = item.get('id', '')
                if not isinstance(data, str) or not data.startswith('data:application/vc+jwt,'):
                    raise ValueError('VP 내부 data URL 형식 오류')
                add(f'{name} / VC {i+1}', data.split(',', 1)[1], depth+1)
    for name, token in named_tokens:
        add(name, token)
    issuers = {d['payload'].get('issuer') for d in docs if isinstance(d['payload'].get('issuer'), str)}
    def resolve(did):
        try:
            return did, resolver(did)
        except Exception as e:
            return did, e
    with ThreadPoolExecutor(max_workers=3) as pool:
        keys = dict(pool.map(resolve, issuers & TRUSTED.keys()))
    checks, limits, cert_cache, status_cache = [], [], {}, {}
    def check(scope, name, status, detail, required=True, code=None):
        checks.append(dict(scope=scope,**result(code or name,name,status,detail,required)))
    def append_rows(scope, rows):
        checks.extend(dict(scope=scope,**r) for r in rows)
    now = now or datetime.now(timezone.utc)
    for d in docs:
        p,h,typ,scope=d['payload'],d['header'],d['kind'],d['file']
        issuer=p.get('issuer')
        doc=keys.get(issuer) if isinstance(issuer,str) else None
        sig,detail=signature(h,p,d['token'],doc)
        check(scope,'서명',sig,detail,code='signature')
        trusted=isinstance(issuer,str) and typ in TRUSTED.get(issuer,set())
        check(scope,'발급자','pass' if trusted else 'fail','명시된 데모 발급자·유형 대조 (공식 신뢰목록 아님)',code='issuer')
        append_rows(scope,[header_check(h,p,typ)])
        ctx=p.get('@context',[])
        if isinstance(ctx,str): ctx=[ctx]
        types=p.get('type',[])
        if isinstance(types,str): types=[types]
        shape=isinstance(ctx,list) and 'https://www.w3.org/ns/credentials/v2' in ctx and trusted
        if typ!='VerifiablePresentation':
            shape=shape and 'VerifiableCredential' in types and isinstance(p.get('credentialSubject'),dict) and is_iri(p.get('id')) and is_iri(p.get('credentialSubject',{}).get('id'))
        check(scope,'기본 구조','pass' if shape else 'fail','VC/VP 유형·context·식별자·subject 구조 확인',code='structure')
        tr,te=time_checks(h,p,now); append_rows(scope,tr); limits.extend(te)
        if typ=='VerifiablePresentation':
            check(scope,'VP 식별자','pass' if is_iri(p.get('id')) else 'warning','샘플 VP는 id가 없을 수 있음; 라이브 인증용 VP로 취급하지 않음',False,'vp_id')
            check(scope,'소유자 인증','not_applicable','파일 가져오기에는 challenge/audience 기반 소유자 인증 미적용',False,'holder_binding')
        elif isinstance(p.get('credentialSubject'),dict):
            st=p['credentialSubject'].get('type')
            if st is None:
                check(scope,'subject 유형','warning','샘플에는 subject.type이 없음; 공식 ICAM 정합성은 별도 보완 필요',False,'subject_type')
            else:
                st=st if isinstance(st,list) else [st]
                check(scope,'subject 유형','pass' if typ in st else 'fail','명시된 subject.type과 이 프로필 유형 대조',True,'subject_type')
        if sig=='pass' and shape:
            append_rows(scope,[schema_check(p,typ)])
            if typ!='VerifiablePresentation':
                sr,se=status_checks(p,doc,policy,now,resource_fetcher,status_cache)
                append_rows(scope,sr); limits.extend(se)
            cache_key=(issuer,h['kid'])
            if cache_key not in cert_cache:
                method=next(m for m in doc['verificationMethod'] if m.get('id')==h['kid'])
                cert_cache[cache_key]=certificate_checks(method,issuer,policy,now,resource_fetcher)
            cr,ce=cert_cache[cache_key]; append_rows(scope,cr)
            if ce: limits.append(ce)
        else:
            check(scope,'후속 검사','unknown','서명·구조 검사 실패로 스키마·인증서·상태 조회를 진행하지 않음',True,'dependent_checks')
    check('세트','공식 SHACL','unknown','포털 자체 부분집합만 적용; 공식 버전별 전체 SHACL 미구현',False,'official_shacl')
    groups = {t: [d for d in docs if d['kind'] == t] for t in REQUIRED}
    complete = (all(len(v) == 1 for v in groups.values()) and
                all(isinstance(d['payload'].get('credentialSubject'), dict) for ds in groups.values() for d in ds))
    check('세트', '구성', 'pass' if complete else 'fail',
          '각 유형의 VC 1개씩 필요: LegalPerson / Issuer / LeiCode / LabelCredential')
    if complete:
        lp = groups['gx:LegalPerson'][0]['payload']
        lrn = groups['gx:LeiCode'][0]['payload']
        cp = groups['gx:LabelCredential'][0]['payload']['credentialSubject']
        ref = lp['credentialSubject'].get('gx:registrationNumber', {})
        linked = isinstance(ref, dict) and ref.get('id') == lrn['credentialSubject'].get('id') and bool(ref.get('id'))
        check('세트', '등록번호 연결', 'pass' if linked else 'fail', 'LegalPerson의 등록번호 참조 ↔ LeiCode의 subject.id')
        refs = cp.get('gx:compliantCredentials', [])
        ref_ids = set()
        hash_ok = isinstance(refs, list) and len(refs) == 3
        for ref in refs if isinstance(refs, list) else []:
            if not isinstance(ref, dict):
                hash_ok = False; continue
            target = next((d for d in docs if d['payload'].get('id') == ref.get('id') and d['kind'] != 'gx:LabelCredential'), None)
            ref_type = ref_credential_type(ref)
            if not target or ref.get('id') in ref_ids or ref_type != target['kind']:
                hash_ok = False; continue
            ref_ids.add(ref['id'])
            sri = ref_digest(ref)
            raw = hashlib.sha256(rfc8785.dumps(target['payload'])).digest()
            accepted = {'sha256-' + raw.hex(), 'sha256-' + base64.b64encode(raw).decode()}
            hash_ok = hash_ok and isinstance(sri, str) and sri in accepted
        expected = {groups[t][0]['payload']['id'] for t in REQUIRED - {'gx:LabelCredential'}}
        check('세트', 'Compliance ID·해시', 'pass' if hash_ok and ref_ids == expected else 'fail',
              'VC 본문 RFC 8785(JCS) → SHA-256 hex; 참조 대상 3개와 대조')
        profile = compliance_profile(policy)
        label, rules = cp.get('gx:labelLevel'), cp.get('gx:rulesVersion')
        rules_present = isinstance(rules, str) and bool(rules.strip())
        check('세트', '검사 프로필', 'pass' if label in profile['label_levels'] and rules_present else 'fail',
              f'labelLevel {"/".join(profile["label_levels"])} 및 rulesVersion 존재 확인; 제출값 {label} / {rules}')
        known = rules in profile['known_rules_versions']
        check('세트', '규칙 버전', 'pass' if known else 'warning',
              f'확인된 버전({", ".join(profile["known_rules_versions"]) or "없음"})' + ('과 일치' if known else f'에 없는 {rules}; Lab 버전 변경으로 보고 연결은 허용'),
              False, 'rules_version')
        tc = groups['gx:Issuer'][0]['payload']
        lp_doc,tc_doc = groups['gx:LegalPerson'][0],groups['gx:Issuer'][0]
        linked_issuer=lp.get('issuer')==tc.get('issuer') and lp_doc['header'].get('kid')==tc_doc['header'].get('kid')
        check('세트','약관 서명자 연결','pass' if linked_issuer else 'fail','LegalPerson / 약관 VC 발급자·서명 키 비교',code='terms_issuer')
        terms=tc['credentialSubject'].get('gaiaxTermsAndConditions')
        check('세트','약관 해시','pass' if isinstance(terms,str) and terms in policy.get('accepted_terms_hashes',[]) else 'fail','운영자가 고정한 샘플 약관 해시와 비교; 법적 대표 권한 증명이 아님',code='terms_hash')
        criteria=cp.get('gx:validatedCriteria',[])
        criteria_ok=(isinstance(criteria,list) and all(isinstance(x,str) for x in criteria) and
                     all(any(x.startswith(CRITERIA_BASE) and x.endswith('/'+sfx) for x in criteria) for sfx in profile['required_criteria_suffixes']))
        check('세트','Compliance 기준','pass' if criteria_ok else 'fail',
              f'서명된 validatedCriteria에 필수 기준({", ".join(profile["required_criteria_suffixes"])}) 포함 여부; 문서 버전 경로는 무관',code='criteria')
        lei=lrn['credentialSubject'].get('schema:leiCode','')
        valid_lei=isinstance(lei,str) and bool(re.fullmatch(r'[A-Z0-9]{18}[0-9]{2}',lei))
        if valid_lei:
            digits=''.join(str(ord(c)-55) if c.isalpha() else c for c in lei)
            valid_lei=int(digits)%97==1
        check('세트','LEI 체크섬','pass' if valid_lei else 'fail','LEI 형식·MOD 97 검사; GLEIF 현재 등록 상태·회사 신원 조회는 별도',code='lei_checksum')
    summary = {}
    if len(groups['gx:LegalPerson']) == 1:
        subject = groups['gx:LegalPerson'][0]['payload'].get('credentialSubject', {})
        address = subject.get('gx:legalAddress', {})
        summary = {'name': subject.get('schema:name'), 'country': address.get('gx:countryCode') if isinstance(address, dict) else None,
                   'subject_id': subject.get('id')}
    check('세트', '데모 조직 속성', 'pass' if isinstance(summary.get('name'), str) and summary['name'] and
          isinstance(summary.get('country'), str) and re.fullmatch('[A-Z]{2}', summary['country']) else 'fail',
          '조직명과 ISO 2자리 국가 코드 필요')
    blocking=[c for c in checks if c['required_for_demo'] and c['status']!='pass']
    counts={status:sum(c['status']==status for c in checks) for status in ('pass','fail','unknown','warning','not_applicable')}
    return {'profile':PROFILE,'eligible_for_demo':not blocking,'production_compliance':False,
            'summary':summary,'checks':checks,'counts':counts,'blocking_checks':blocking,
            'verified_at':now.isoformat(),'valid_until':min(limits).isoformat() if limits else None,
            'has_credential_status':any('credentialStatus' in d['payload'] for d in docs),
            'documents':[{k:v for k,v in d.items() if k!='token'} for d in docs],
            'notice':'포털 데모 검증 결과입니다. 공식 Gaia-X 인증·전체 스키마 검증·회사 대표 권한을 증명하지 않습니다.'}
