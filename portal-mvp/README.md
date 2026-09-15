# Gaia-X Portal · Loire demo v2

첨부 프로젝트의 VC 검증을 보완한 PoC입니다. 외부에서 발급받은 VC/VP를 가져오며, 이 포털이 VC를 발급하지는 않습니다. 기존 회원가입, 로그인, 자격증명 가져오기, 데모 참여자 연결, 국가 정책에 따른 서비스 요청 흐름을 유지합니다.

**이 프로젝트의 통과 판정은 `loire-demo-v2` 데모 정책을 만족한다는 뜻입니다. 공식 Gaia-X 적합성 인증 완료를 의미하지 않습니다.**

## 실행

Python 3.12에서 테스트했습니다. Python 3.11 이상을 사용하세요.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python portal.py --host 127.0.0.1 --port 8000
```

브라우저에서 `http://localhost:8000`에 접속합니다. Windows에서는 `.venv\Scripts\activate`를 사용하세요. `requirements.txt`는 직접 의존성, `requirements-lock.txt`는 테스트 환경의 전체 고정 버전이며 테스트 도구도 포함합니다.

기존 설치를 업데이트할 때는 기존 `data/` 데이터베이스를 보존하고, 이번 ZIP의 코드·설정·`schemas/`를 함께 적용하세요. `credentials.py`만 교체하면 동작하지 않습니다. 저장된 v1 검증 결과는 재검증 후 연결해야 합니다. 서버를 재시작한 뒤 Credentials 화면의 **다시 검증**을 누르세요.

호스트·Origin은 기존 `portal.py`의 제한을 유지했습니다. 다른 호스트/포트로 운영한다면 `PUBLIC_HOSTS`/`ORIGINS`/CORS 설정도 함께 조정해야 합니다.

## 이번에 추가·강화한 검사

| 영역 | 검증 내용 |
| --- | --- |
| JWT/DID | 헤더 `iss`와 본문 `issuer`, `typ`/`cty` 조합, 허용 알고리즘, DID 문서 ID, 중복 키 ID, controller, assertionMethod, JWK 용도와 RSA 키 길이 |
| 기간 | VC `validFrom`/`validUntil`, 본문 `exp`/`nbf`/`iat`, 알려진 Lab VC의 밀리초 헤더 시간과 VC 날짜 일치 |
| 인증서 | DID JWK와 leaf 공개키 일치, 체인 전체 기간, 인접 인증서 서명, CA/KeyUsage/pathLen 기본 제약, 루트 자기서명, 운영자가 고정한 데모 루트 지문 |
| 스키마 | 로컬 고정 JSON-LD context + 포털 자체 SHACL 부분집합으로 LegalPerson·약관·LEI·Compliance 필수 속성 검사 |
| VC 상태 | 등록된 URL의 서명된 BitstringStatusListCredential로 폐기·정지 검사, 목록 자체의 서명·발급자·ID·기간·인증서 검증 |
| 세트 의미 | 기존 Compliance JCS 해시 검증 유지, 약관 서명자/키 연결·약관 해시·필수 criteria·LEI 체크섬 추가 |
| 접근 판단 | 필수 검사 실패/확인 불가 시 연결 차단, VC/JWT/인증서/상태 목록의 가장 이른 만료 적용, 구버전 보고서 및 상태 정보 재검증 |
| 화면 | 통과/실패/확인 불가/주의/해당 없음 구분, 필수 여부, 결과 필터, 검증 시각과 유효 한계 표시 |

상세 내용과 한계는 `docs/CHANGES.md`, 실행 결과는 `docs/TEST_RESULTS.md`를 보세요.

## 검증 정책 설정

기본 정책은 `verification-policy.json`입니다. 다른 위치의 정책은 서버 환경변수로 지정합니다.

```bash
export PORTAL_VERIFICATION_POLICY=/absolute/path/verification-policy.json
```

- `certificate_sources`: 각 데모 issuer가 사용할 수 있는 정확한 인증서 URL과 데모 루트 SHA-256 지문입니다. 검증 요청에서 받은 루트를 자동으로 신뢰하지 않습니다. Lab 루트 및 공개 CA 루트가 섞여 있어도 공식 Gaia-X trust anchor 인정은 별도입니다.
- `accepted_terms_hashes`: 이 PoC가 수용하는 샘플 약관 해시입니다. 약관 원문/버전을 확인한 후 운영자가 변경합니다.
- `required_criteria`: Compliance VC에 포함되어야 하는 서명된 기준 ID입니다. 현재 PA1.1을 요구합니다. 기준에 대한 외부 심사를 포털이 재수행하는 것은 아닙니다.
- `status_list_urls`: `{ "정확한 HTTPS 목록 URL": "해당 VC의 issuer DID" }` 형태입니다. 기본값은 빈 객체입니다. 제공된 샘플에 상태 목록 정보가 없으므로 임의 목록을 추가하지 않았습니다.

인증서 교체 시 leaf 키 변경은 현재 DID와 일치해야 하고, 루트 변경은 운영자가 출처를 확인한 뒤 지문을 갱신해야 합니다. 유효성 검사를 끄는 방식으로 해결하지 마세요. 런타임 context는 네트워크에서 재다운로드하지 않으며, SHACL/context 변경 시 `schemas/manifest.json`의 SHA-256도 검토 후 갱신하고 서버를 재시작해야 합니다.

## 상태 목록 지원 범위

지원: W3C BitstringStatusListEntry의 `revocation`/`suspension`, 1-bit 상태, compact JWT 또는 EnvelopedVerifiableCredential로 감싼 JWT 목록. 목록은 VC와 같은 issuer가 서명해야 하며 W3C VC v2 context만 사용합니다. 목록의 `validFrom`은 이 프로필에서 필수이며 `validUntil`이 있으면 기간 제한에 포함합니다. encodedList는 `u` multibase + base64url + gzip이고 MSB-first로 읽습니다.

미지원: Data Integrity proof 목록, 별도 위임 발급자, 재귀 상태 목록, 1-bit가 아닌 상태, 기타 폐기 규격. 해당 정보가 제출되면 확인 불가/실패로 연결을 차단합니다.

`credentialStatus` **필드가 없는 경우만** 비필수 `unknown`으로 남겨 데모 연결을 허용할 수 있습니다. 필드가 있으나 목록이 미등록·만료·조회 실패·검증 실패인 경우에는 필수 검사가 통과하지 않았으므로 연결하지 않습니다.

원격 조회는 정확한 URL allowlist, HTTPS, 리다이렉트 금지, 8초 timeout, DID/인증서 256 KB 및 목록 JWT 512 KB 제한을 적용합니다. 압축 해제 목록은 16 KB~1 MB입니다. URL allowlist는 관리자 설정이며 DNS 주소를 고정하는 구현은 아닙니다. TLS 검증은 유지되며 서버 환경의 HTTP(S) 프록시를 따릅니다.

## 테스트

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
node tests/dashboard-smoke.cjs
```

Python 테스트는 매번 임시 RSA 키/인증서/서명 VC를 만들며 외부 네트워크가 필요 없습니다. Node 테스트는 화면 렌더 함수·필터·출력 이스케이프를 확인합니다. 실제 브라우저 시각 테스트는 포함하지 않습니다. 사용자 JWT·개인키·DB는 배포 ZIP에 포함하지 않았습니다.

## Production 전환에 남은 작업

공식 버전별 전체 SHACL, 공식 Gaia-X 신뢰목록과 GXDCH 인정, EV/eIDAS와 법인 신원 연결, 완전한 PKIX 인증서 경로 검증 및 CRL/OCSP, GLEIF 현재 등록 상태 확인, challenge/audience를 이용한 소유자·대표권 증명은 남아 있습니다. 이 파일 가져오기 흐름은 로그인 또는 실시간 VP 인증 프로토콜을 대체하지 않습니다.

따라서 현재 단계는 **“서명·구조·연결·기간·일부 신뢰 및 상태 검사를 구현하고, 미검증 영역을 분리한 Gaia-X 검증 PoC”**로 설명하는 것이 정확합니다. EV-SSL이나 LEI를 구매하는 것만으로 production 검증이 완성되지는 않습니다.
