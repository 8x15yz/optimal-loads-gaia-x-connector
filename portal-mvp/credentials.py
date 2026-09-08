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

MAX_FILE = 2_000_000
MAX_TOTAL = 8_000_000
PROFILE = 'loire-demo-v1'
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
    if 'VerifiablePresentation' in types:
        return 'VerifiablePresentation'
    return next((x for x in types if x in REQUIRED), 'Unknown')

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
    with httpx.Client(timeout=5, follow_redirects=False) as client:
        with client.stream('GET', url) as r:
            r.raise_for_status()
            data = b''
            for part in r.iter_bytes():
                data += part
                if len(data) > 256_000:
                    raise ValueError('DID 문서 크기 제한 초과')
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
    kid = header.get('kid', '')
    if not isinstance(kid, str) or not kid.startswith(str(issuer) + '#'):
        return 'fail', 'kid와 issuer 관계 불일치'
    method = next((m for m in doc.get('verificationMethod', []) if m.get('id') == kid), None)
    if not method or method.get('controller') != issuer:
        return 'fail', '검증 키 또는 controller 불일치'
    purposes = doc.get('assertionMethod', [])
    if kid not in [m.get('id') if isinstance(m, dict) else m for m in purposes]:
        return 'fail', 'assertionMethod로 허용되지 않은 키'
    if header.get('alg') not in {'RS256', 'PS256'}:
        return 'fail', '이 가져오기 프로필에서 허용하지 않는 알고리즘'
    try:
        key = jwt.PyJWK.from_dict(method['publicKeyJwk'], algorithm=header['alg']).key
        # Deliberately only cryptographic validation here. VC dates checked separately.
        jwt.decode(token, key, algorithms=[header['alg']], options={
            'verify_exp': False, 'verify_iat': False, 'verify_nbf': False,
            'verify_aud': False, 'verify_iss': False, 'verify_sub': False,
            'verify_jti': False})
        return 'pass', '공개키로 원본 JWT 서명 검증 성공'
    except Exception as e:
        return 'fail', '서명 검증 실패: ' + type(e).__name__

def date_value(value):
    if not isinstance(value, str):
        raise ValueError('시간 문자열 필요')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('시간대 필요')
    return dt

def inspect_set(named_tokens, resolver=fetch_document):
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
    checks = []
    def check(scope, name, status, detail):
        checks.append({'scope': scope, 'name': name, 'status': status, 'detail': detail})
    now = datetime.now(timezone.utc)
    for d in docs:
        p, h, typ = d['payload'], d['header'], d['kind']
        scope = d['file']
        issuer = p.get('issuer')
        sig, detail = signature(h, p, d['token'], keys.get(issuer) if isinstance(issuer, str) else None)
        check(scope, '서명', sig, detail)
        trusted = isinstance(issuer, str) and typ in TRUSTED.get(issuer, set())
        check(scope, '발급자', 'pass' if trusted else 'fail',
              '명시된 데모 발급자·자격증명 유형' if trusted else '이 유형에 인정하지 않는 발급자')
        ctx = p.get('@context', [])
        if isinstance(ctx, str): ctx = [ctx]
        shape = isinstance(ctx, list) and 'https://www.w3.org/ns/credentials/v2' in ctx and trusted
        if typ != 'VerifiablePresentation':
            shape = (shape and isinstance(p.get('credentialSubject'), dict) and isinstance(p.get('id'), str)
                     and h.get('typ') in {'vc+jwt', 'vc+ld+jwt'} and h.get('cty') in {'vc', 'vc+ld'})
        else:
            shape = shape and h.get('typ') == 'vp+jwt'
        check(scope, '기본 구조', 'pass' if shape else 'fail', 'Loire 샘플 프로필의 필수 필드 확인 (SHACL 전체 검증 아님)')
        try:
            start, end = date_value(p.get('validFrom')), date_value(p.get('validUntil'))
            valid = start <= now < end
            check(scope, '유효기간', 'pass' if valid else 'fail', f"{p.get('validFrom')} ~ {p.get('validUntil')}")
        except (ValueError, TypeError):
            check(scope, '유효기간', 'fail', '시간대가 있는 validFrom / validUntil 필요')
        check(scope, '폐기·정지', 'unknown',
              'credentialStatus 조회는 이번 MVP에서 미구현' if p.get('credentialStatus') else 'credentialStatus가 없어 확인 불가')
    check('세트', 'SHACL', 'unknown', '공식 SHACL·인증서 신뢰 체인 검증은 이번 MVP 범위 밖')
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
            if not target or ref.get('id') in ref_ids or ref.get('type') != target['kind']:
                hash_ok = False; continue
            ref_ids.add(ref['id'])
            digest = 'sha256-' + hashlib.sha256(rfc8785.dumps(target['payload'])).hexdigest()
            hash_ok = hash_ok and digest == ref.get('gx:digestSRI')
        expected = {groups[t][0]['payload']['id'] for t in REQUIRED - {'gx:LabelCredential'}}
        check('세트', 'Compliance ID·해시', 'pass' if hash_ok and ref_ids == expected else 'fail',
              'VC 본문 RFC 8785(JCS) → SHA-256 hex; 참조 대상 3개와 대조')
        check('세트', '검사 프로필', 'pass' if cp.get('gx:labelLevel') == 'SC' and cp.get('gx:rulesVersion') == 'CD25.10' else 'fail',
              '이번 데모는 SC / CD25.10 샘플 프로필을 명시적으로 수용')
    summary = {}
    if len(groups['gx:LegalPerson']) == 1:
        subject = groups['gx:LegalPerson'][0]['payload'].get('credentialSubject', {})
        address = subject.get('gx:legalAddress', {})
        summary = {'name': subject.get('schema:name'), 'country': address.get('gx:countryCode') if isinstance(address, dict) else None,
                   'subject_id': subject.get('id')}
    check('세트', '데모 조직 속성', 'pass' if isinstance(summary.get('name'), str) and summary['name'] and
          isinstance(summary.get('country'), str) and re.fullmatch('[A-Z]{2}', summary['country']) else 'fail',
          '조직명과 ISO 2자리 국가 코드 필요')
    blocking_unknown = any(c['name'] == '서명' and c['status'] != 'pass' for c in checks)
    eligible = not any(c['status'] == 'fail' for c in checks) and not blocking_unknown
    return {'profile': PROFILE, 'eligible_for_demo': eligible, 'production_compliance': False,
            'summary': summary, 'checks': checks,
            'documents': [{k: v for k, v in d.items() if k != 'token'} for d in docs],
            'notice': '서명 확인과 데모 수용 결과입니다. 실제 회사 신원·공식 Gaia-X 적합성 또는 전체 스키마 검증을 의미하지 않습니다.'}
