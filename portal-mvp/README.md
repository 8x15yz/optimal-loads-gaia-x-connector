# Credential Portal — 가벼운 로컬 MVP

기존 FastAPI + HTML/JS 포털을 바탕으로, 외부에서 발급받은 credentials 가져오기와 검증을 추가했습니다.
외부 DB 서버, 프론트엔드 빌드, Docker, 계정 시스템이 필요하지 않습니다.

## 실행

Python 3.10 이상을 사용하세요. 압축을 해제한 `portal-mvp` 폴더에서:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe portal.py --port 8001 --name "BLUEMAP Demo"
```

macOS / Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python portal.py --port 8001 --name "BLUEMAP Demo"
```

브라우저에서 http://localhost:8001 을 여세요. HTML 파일을 직접 열지 않습니다.
서버는 127.0.0.1에만 바인딩합니다. 이 버전은 한 PC의 로컬 데모용이며 외부 배포용 로그인·운영자 인증은 포함하지 않습니다.

## 계정과 자격증명

이 버전은 로그인 계정 개념을 추가했습니다. 계정 하나에 자격증명(VC/VP) 세트를 여러 개 가져와 연결할 수 있고,
가져온 세트들은 로그아웃 후 다시 로그인해도 그대로 남아 있습니다 (**Account** 탭 → 아이디/비밀번호로 회원가입·로그인).
계정은 포털(포트)마다 별도의 SQLite 파일에 저장되므로, 8001과 8002 두 포털을 함께 띄운 경우 각 포털에 따로 가입·로그인해야 합니다.
비밀번호는 PBKDF2(HMAC-SHA256, 200,000회)로 해시해 저장하며 평문으로 저장하지 않습니다.

**Credentials** 탭에서 파일을 가져오면 현재 로그인한 계정에 새 항목으로 추가됩니다(기존 항목을 덮어쓰지 않음).
"내 계정에 연결된 자격증명" 목록에서 각 세트별로 **다시 검증**하거나, 그 중 하나를 골라 **데모 참여자로 연결**할 수 있습니다.
다른 계정으로 로그인한 상태에서는 남의 계정에 연결된 자격증명을 조회·재검증·연결할 수 없습니다(서버가 소유권을 확인함).

## 가장 짧은 시연 순서

1. **Account**에서 회원가입 후 로그인합니다.
2. **Credentials**에서 `Signed Verifiable Presentation.jwt`와 `Compliance Verifiable Credential.jwt`를 함께 선택합니다.
3. **가져오기 · 검증**을 누릅니다. VC 3개가 VP 안에서 추출되고, 로그인한 계정에 연결됩니다.
4. 검사별 `통과 / 실패 / 확인 불가`를 확인합니다. 원본 헤더·본문도 펼쳐볼 수 있습니다.
5. "내 계정에 연결된 자격증명" 목록에서 핵심 검사가 통과한 항목을 **데모 참여자로 연결**합니다. 1시간짜리 무작위 세션 토큰이 생성됩니다.
6. **Services**에서 기본값 그대로 서비스 등록: `Busan Weather Demo`, `KR`, `demo://weather`.
7. **Catalog**에서 조회합니다. (Catalog는 계정 로그인이 아니라 5번의 데모 연결을 필요로 합니다.)
8. **Request**에서 서비스를 선택하고 요청합니다. 서버가 자격증명과 정책을 다시 확인한 뒤 고정 기상 샘플을 반환합니다.
9. 국가를 `DE`로 설정한 서비스를 등록하면, `KR` 참여자의 요청은 403으로 차단되고 화면에도 실패로 표시됩니다.

서명 공개키 조회 실패 시에도 파일을 읽고 나머지 검사 결과를 볼 수 있지만, 데모 연결은 차단됩니다.
네트워크 연결을 확인한 뒤 **다시 검증**을 누르세요. 서명 검증을 건너뛰는 옵션은 없습니다.

ZIP + VP 또는 개별 VC 4개도 입력할 수 있습니다. ZIP에는 JWT만 넣으세요.
모든 파일을 넣으면 같은 JWT는 중복 제거됩니다. 같은 ID인데 JWT가 다르면 충돌로 거부합니다.
브라우저 새로고침 후에는 계정에 다시 로그인해야 합니다(계정 토큰과 데모 세션 토큰 모두 브라우저 메모리에만 보관). 로그인만 다시 하면 가져온 자격증명 목록은 서버에 그대로 남아 있어 재가져오기는 필요 없습니다.
서비스·가져오기 기록·데모 접근 승인·계정 정보는 자동 생성되는 `data/portal-8001.sqlite3`에 저장됩니다.

## 두 포털로 시연

다른 터미널에서 아래를 실행하면 저장소가 분리된 두 번째 포털이 생깁니다.

```bash
python portal.py --port 8002 --name "GMT Demo"
```

1. 8001 포털의 Services에서 제공할 서비스를 등록합니다.
2. 8002 포털을 열어 Credentials의 **제출할 포털**을 `localhost:8001`로 선택합니다.
3. 자격증명을 업로드하고 연결합니다. 검증과 데모 참여자 등록은 수신자인 8001에서 수행됩니다.
4. 8002의 Catalog / Request에서 8001의 서비스를 조회·요청합니다.

이 버전의 통신은 브라우저 → 선택한 제공자 포털입니다. 소비자 백엔드가 별도 키로 요청을 서명하는 M2M 방식은 아직 아닙니다.
동일한 credential 세트를 양쪽에서 사용하면 같은 데모 주체로 연결됩니다. 서로 다른 회사 신원으로 바뀌는 것은 아닙니다.

## 검증 범위

| 항목 | 구현 |
|---|---|
| VC / VP 분류 | JWT 헤더·본문 파싱; VP의 Enveloped VC 추출 |
| 서명 | 원본 JWT를 PyJWT + cryptography로 RS256 / PS256 검증 |
| 공개키 | 아래 허용 DID에 한해 HTTPS DID 문서를 조회; kid, controller, assertionMethod 확인 |
| 발급자 신뢰 | 코드에 명시한 데모 발급자와 자격증명 유형 조합만 수용 |
| 시간 | 본문의 validFrom / validUntil을 시간대 포함으로 검사 |
| 기본 구조 | VC v2 context, 타입, subject, id, 프로필에 필요한 필드 확인 |
| 문서 연결 | LegalPerson → LeiCode subject ID 참조 확인 |
| Compliance | 참조 대상 3개 ID / 타입 / JCS SHA-256 해시 대조, SC / CD25.10 확인 |
| 폐기·정지 | 미구현. 상태 필드 부재/조회 미구현을 ‘확인 불가’로 표시 |
| 공식 SHACL / X.509 신뢰 체인 | 미구현. 전체 적합성 검증으로 표시하지 않음 |

가져오기 프로필 이름은 `loire-demo-v1`입니다. Gaia-X 전체 버전에 대한 범용 검증기가 아닙니다.
검사 프로필은 사용자가 제공한 Loire Wizard 샘플의 `SC`, `CD25.10`에 고정했습니다.
그 외 버전은 자동으로 신뢰하지 않고 검사 실패로 표시합니다.

허용 발급자와 조회 위치:

| DID | HTTPS DID 문서 |
|---|---|
| `did:web:vc-jwt.io` | `https://vc-jwt.io/.well-known/did.json` |
| `did:web:registrationnumber.notary.lab.gaia-x.eu:v2` | `https://registrationnumber.notary.lab.gaia-x.eu/v2/did.json` |
| `did:web:compliance.lab.gaia-x.eu:development` | `https://compliance.lab.gaia-x.eu/development/did.json` |

임의 DID, 자동 리다이렉트, 알 수 없는 서명 알고리즘은 수용하지 않습니다.
공개키 조회 타임아웃은 연결/읽기 등 각 네트워크 단계 기준 5초입니다.
회사 자체 DID, SSL 또는 개인키는 **이번에 받은 파일의 서명 검사**에 필요하지 않습니다.
검증하는 것은 해당 외부 서명자의 키입니다. 공개키가 바뀌거나 더 이상 제공되지 않으면 확인 불가/실패할 수 있습니다.

본문의 `exp`가 아니라 `validFrom / validUntil`을 확인합니다.
특히 샘플의 일부 iat / exp는 JWT 헤더에 존재하므로 일반 JWT 라이브러리의 만료 검사로 대체할 수 없습니다.
해시는 VC 본문을 RFC 8785(JCS)로 정규화한 바이트에 SHA-256을 적용한 hex 값을 사용합니다.
사용자가 제공한 VC 3개에 대해 이 계산 결과가 Compliance VC의 참조 해시와 일치함을 확인했습니다.
다른 버전의 digest 프로필을 임의로 추측해 통과시키지는 않습니다.

## 신뢰와 데모 연결의 의미

서명·발급자·기본 구조·기간·세트 연결이 통과해야 세션을 발급합니다.
폐기·정지 및 공식 SHACL 전체 검증의 미구현은 표시한 채 제한된 데모에서만 수용합니다.
`production_compliance`는 항상 false입니다. 공개키가 없거나 서명이 틀린 경우는 연결하지 않습니다.

파일 업로드는 회사 대표 권한 증명이 아닙니다. 업로더와 조직의 관계는 로컬 운영자가 테스트용으로 연결한 것으로 취급합니다.
수신 포털이 생성하는 무작위 토큰은 Gaia-X VC나 VP가 아니라 이 데모의 접근 세션입니다.
사용자가 consumer_id를 임의 입력해 권한을 얻을 수 없도록 요청 주체는 서버의 세션에서 결정합니다.
토큰은 DB에 해시로 저장합니다. 업로드 원본 JWT는 로컬 SQLite에 보관합니다.

## 서비스·계약·전송 범위

- 카탈로그는 연결된 세션으로 조회합니다. 서비스마다 국가 조건을 표시합니다.
- `/negotiate`에서 자격증명을 다시 검증하고 LegalPerson의 `gx:legalAddress.gx:countryCode`를 정책과 비교합니다.
- 조건이 맞으면 서버가 **데모 접근 승인**을 발급합니다. 승인 유효기간은 최대 15분이며 세션 만료를 넘지 않습니다.
- `/transfer`도 세션, 당사자, 승인 만료, 현재 정책, credentials를 다시 검증합니다.
- 양측 서명 DAC, DUA/Notary, Party Credential 위임, 자체 DID/키, 실시간 VP challenge/nonce, 자동 스케줄링은 후속 단계입니다.
- 기존의 EdDSA 자체 Membership VC 발급 기능·키 파일은 제거했습니다.

## 실제 Weather API 연결

기본값은 네트워크가 필요 없는 고정 샘플입니다. 실제 API를 쓰려면 서버 실행 전에 허용 origin을 설정하세요.

Windows PowerShell 예시:

```powershell
$env:PORTAL_ALLOWED_DATA_ORIGINS = "https://weather-api.example.com"
.\.venv\Scripts\python.exe portal.py --port 8001
```

macOS / Linux 예시:

```bash
PORTAL_ALLOWED_DATA_ORIGINS="https://weather-api.example.com" .venv/bin/python portal.py
```

Services의 데이터 URL에는 위 origin 아래 실제 JSON API 주소를 입력합니다.
여러 origin은 쉼표로 구분합니다. 프로토콜·호스트·포트가 정확히 일치해야 합니다.
API 인증 헤더 설정은 아직 지원하지 않습니다. 최대 응답 5 MB, 자동 리다이렉트 금지입니다.
허용 목록은 로컬 운영자가 신뢰하는 API로만 설정합니다. 이 기능은 범용 인터넷 프록시가 아닙니다.

## 파일 구성

- `portal.py`: API, SQLite, 계정·데모 세션, 서비스·전송
- `accounts.py`: 계정 비밀번호 해시·검증 (PBKDF2, 외부 의존성 없음)
- `credentials.py`: 파일 파싱, DID 공개키 조회, 서명·기간·연결 검증
- `dashboard.html`: 기존 포털 스타일을 유지한 화면 (별도 JS 프레임워크 없음)
- `requirements.txt`: 실행 의존성
- `tests/test_portal.py`: 오프라인 합성 키·자격증명·계정 기반 회귀 테스트

## 테스트

```bash
python -m pip install pytest
python -m pytest -q tests
```

테스트는 매번 생성한 RSA 키와 합성 자격증명을 사용하고 DID 조회를 테스트 함수로 대체합니다.
실제 Gaia-X VC가 아니라 파서·서명 검증·정책·접근 제어 로직을 검증하는 용도입니다.
제공된 실제 credential 파일은 코드 ZIP에 포함하지 않았습니다. 기존 다운로드 파일을 업로드하세요.

## 검증 기록

- 오프라인 백엔드 회귀 테스트: 서명 정상/변조, 만료, 해시 불일치, 누락, 중복 충돌, 공개키 조회 실패, 국가 정책, 인증 없는 전송, 다른 참여자 승인 사용, 전송 시 재검증, 계정 가입·로그인·로그아웃, 계정 간 자격증명 소유권 격리 등 (`pytest -q tests`, 17개 통과 확인).
- 제공된 실제 샘플: VC/VP 5개 고유 문서 추출·중복 관계 및 세 개의 Compliance 해시 일치 확인. 공개키를 조회하지 않는 검사에서는 서명을 확인 불가로 표시하고 연결을 차단함을 확인.
- UI JavaScript 구문 검사 통과. 브라우저 실행 파일을 확보하지 못해 실제 브라우저 렌더링·클릭 시연은 미확인.
- 실제 외부 DID 서명 검증: 작업 환경에서 공개키 네트워크 조회가 완료되지 않아 **통과 여부 미확인**. 실행 환경에서 ‘다시 검증’으로 확인해야 합니다.

## 참조

- https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/gaia-x_credentials/
- https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/semantic_model/
- https://www.rfc-editor.org/rfc/rfc8785
