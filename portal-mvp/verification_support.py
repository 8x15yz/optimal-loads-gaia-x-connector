"""Bounded resource retrieval and explicitly pinned DEMO certificate validation.
Not a full RFC 5280 path validator or Gaia-X accreditation check.
"""
import base64
import ipaddress
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

import httpx
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID

ROOT = Path(__file__).resolve().parent

def load_policy():
    p = json.loads(Path(os.getenv('PORTAL_VERIFICATION_POLICY', str(ROOT / 'verification-policy.json'))).read_text())
    if p.get('profile') != 'loire-demo-v2':
        raise ValueError('지원하지 않는 검증 정책 프로필')
    return p

def remote_bytes(url, allowed, max_bytes=256_000):
    if not isinstance(url, str) or url not in allowed:
        raise ValueError('관리자가 지정한 정확한 URL만 조회할 수 있습니다')
    u = urlsplit(url)
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.fragment or u.port not in (None,443):
        raise ValueError('HTTPS URL 형식 오류')
    if u.hostname.lower() in {'localhost','metadata.google.internal'} or u.hostname.endswith(('.local','.internal')):
        raise ValueError('내부 호스트 거부')
    try:
        addr = ipaddress.ip_address(u.hostname)
    except ValueError:
        addr = None
    if addr is not None and not addr.is_global:
        raise ValueError('내부 IP 거부')
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    # Standard TLS verification and administrator HTTP(S) proxy environment apply.
    # No redirects, embedded credentials or arbitrary credential-supplied URLs.
    with build_opener(NoRedirect()).open(Request(url,headers={'Accept':'application/json, application/jwt, application/x-pem-file'}),timeout=8) as response:
        body=response.read(max_bytes+1)
        if len(body)>max_bytes:
            raise ValueError('원격 응답 크기 제한 초과')
    return bytes(body)

def result(code, name, status, detail, required=True):
    return dict(code=code,name=name,status=status,detail=detail,required_for_demo=required)

def certificate_checks(method, issuer, policy, now, fetcher=remote_bytes):
    rows, expiry = [], None
    def row(code,name,ok,detail):
        rows.append(result(code,name,'pass' if ok else 'fail',detail))
    try:
        jwk = method['publicKeyJwk']
        src = policy.get('certificate_sources',{}).get(issuer,{})
        if jwk.get('x5c'):
            if not isinstance(jwk['x5c'],list) or not 1 <= len(jwk['x5c']) <= 8:
                raise ValueError('x5c 개수 제한')
            chain = [x509.load_der_x509_certificate(base64.b64decode(v,validate=True)) for v in jwk['x5c']]
        else:
            url = jwk.get('x5u') or method.get('x5u')
            raw = fetcher(url,src.get('urls',[]),256_000)
            chain = x509.load_pem_x509_certificates(raw)
        if not 1 <= len(chain) <= 8: raise ValueError('인증서 체인 개수 오류')
        expected = jwt.PyJWK.from_dict(jwk,algorithm='RS256').key
        fmt = (serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
        row('cert_key','인증서 공개키',chain[0].public_key().public_bytes(*fmt)==expected.public_bytes(*fmt),'DID JWK ↔ leaf 인증서 공개키 비교')
        expiry = min(c.not_valid_after_utc for c in chain)
        row('cert_dates','인증서 유효기간',all(c.not_valid_before_utc<=now<c.not_valid_after_utc for c in chain),'체인 내 모든 인증서 기간 검사; 가장 이른 만료: '+expiry.isoformat())
        fps = [c.fingerprint(hashes.SHA256()).hex() for c in chain]
        if len(set(fps)) != len(fps): raise ValueError('중복 인증서')
        for i,c in enumerate(chain):
            if c.signature_hash_algorithm is None or c.signature_hash_algorithm.name in ('md5','sha1'):
                raise ValueError('약하거나 미지원 인증서 서명 알고리즘')
            key=c.public_key()
            if isinstance(key,rsa.RSAPublicKey) and key.key_size<2048: raise ValueError('RSA 2048 bit 미만')
            if i:
                bc=c.extensions.get_extension_for_class(x509.BasicConstraints).value
                if not bc.ca: raise ValueError('상위 인증서가 CA가 아님')
                if bc.path_length is not None and sum(1 for d in chain[1:i] if d.subject!=d.issuer)>bc.path_length:
                    raise ValueError('CA pathLen 초과')
            try:
                ku=c.extensions.get_extension_for_class(x509.KeyUsage).value
                if (i==0 and not ku.digital_signature) or (i>0 and not ku.key_cert_sign): raise ValueError('KeyUsage 불일치')
            except x509.ExtensionNotFound: pass
            if i+1<len(chain): c.verify_directly_issued_by(chain[i+1])
        chain[-1].verify_directly_issued_by(chain[-1])
        row('cert_chain','인증서 체인 서명',True,'인접 인증서 발급·서명, CA 기본 제약, 루트 자기서명 확인 (전체 PKIX 아님)')
        unsupported = any(e.critical and e.oid not in {ExtensionOID.BASIC_CONSTRAINTS,ExtensionOID.KEY_USAGE,ExtensionOID.SUBJECT_ALTERNATIVE_NAME} for c in chain for e in c.extensions)
        rows.append(result('cert_extensions','인증서 확장','unknown' if unsupported else 'pass','미지원 critical 확장은 데모 연결 차단' if unsupported else '이 프로필이 지원하는 critical 확장 범위'))
        row('demo_root','데모 루트 고정',fps[-1] in src.get('demo_root_sha256',[]),'운영자가 별도로 고정한 데모 루트 SHA-256 대조; 공식 Gaia-X trust anchor 인정이 아님')
    except (httpx.HTTPError,OSError) as e:
        rows.append(result('certificate','인증서 조회','unknown','인증서 조회 실패: '+type(e).__name__))
    except Exception as e:
        rows.append(result('certificate','인증서 검증','fail',str(e)[:180] or type(e).__name__))
    rows.append(result('certificate_revocation','인증서 CRL/OCSP','unknown','인증서 폐기·정지 조회 미구현',False))
    rows.append(result('official_trust','공식 Gaia-X 신뢰','unknown','공식 신뢰목록·GXDCH 인정 및 EV/eIDAS 정책은 검증하지 않음',False))
    return rows,expiry
