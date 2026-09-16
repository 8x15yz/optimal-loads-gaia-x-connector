# Management Console PoC — 0.4

기존 VC 검증기를 유지하면서, 한 계정이 **VC 등록 → 참여 세션 연결 → 서비스 계약 → 고정 주소 데이터 조회 → 초기화 → 재연결**을 실행할 수 있도록 추가했습니다.

## 실행

Python 3.11 이상. 기존 실행 방법과 SQLite DB 경로를 유지합니다.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python portal.py --port 8000
```

브라우저에서 `http://localhost:8000`을 엽니다. 처음 가입한 사용자가 자동으로 관리자가 되지는 않습니다.

### 관리자 최초 생성 (서버에서만)

서버를 종료한 상태에서, 일반 가입을 사용하지 않고 아래 명령으로 관리자 계정을 생성합니다. 기존 계정 이름을 지정하면 비밀번호가 재설정되고 해당 계정의 로그인 세션이 해제됩니다. **생성 명령은 최초 한 번만 실행**하세요.

```bash
python manage_admin.py --username admin --port 8000
```

비밀번호는 표시되지 않는 입력창으로 받습니다. 이후 서버를 실행할 때 관리자 이름을 지정합니다.

Windows PowerShell:

```powershell
$env:PORTAL_ADMIN_USERS = "admin"
python portal.py --port 8000
```

macOS/Linux:

```bash
PORTAL_ADMIN_USERS=admin python portal.py --port 8000
```

서버 실행 포트와 관리자 생성 명령의 포트가 같아야 동일 DB를 사용합니다. 관리자 권한은 서버의 `PORTAL_ADMIN_USERS`로 결정하며 콘솔에서 권한 승격은 제공하지 않습니다. 복수 관리자는 쉼표로 구분할 수 있습니다.

## 시연 순서

1. 관리자 로그인 → **Admin Console** → `demo://weather`와 국가 `KR`로 Weather Demo 서비스 등록.
2. 로그아웃 → 소비자 계정 가입/로그인.
3. **VC 관리** → 실제 non-production VC/VP 파일 업로드 → 검증 항목 확인.
4. 해당 VC 세트의 **세션 연결** 클릭. 기존 검증기를 다시 실행하며, 차단 항목이 있으면 연결되지 않습니다.
5. **서비스 · 데이터 연결** → 국가 정책에 맞는 서비스 계약.
6. **ping 테스트**, **데이터 테스트** 실행. 샘플 JSON 응답 확인.
7. **활동 및 검증 로그** → 해당 작업 펼침 → 세부 검사 결과 확인.
8. **연결 현황** → 세션 종료·초기화. 같은 주소의 ping/데이터 조회가 거부되는지 확인.
9. 동일 VC로 재연결 후 서비스를 다시 계약. 같은 접속 주소로 다시 조회 가능.

**테스트용 통과 VC를 프로그램에 내장하지 않았습니다.** 제공된 VC가 기존 검증기를 통과해야 실제 콘솔에서도 연결됩니다. API 통합 테스트는 성공 보고서를 테스트 안에서만 대체하며, 실행 서버에 검증 우회 기능은 없습니다.

## 콘솔 기능

| 영역 | 핵심 기능 |
|---|---|
| 연결 현황 | VC 세트 수, 참여 세션 만료, 활성 계약 수, 세션 초기화, 키 재발급 |
| VC 관리 | 파일 업로드, 세트별 재검증·연결·삭제, 문서별 상세 검사 결과 |
| 서비스 · 데이터 연결 | 서비스 계약·해지, 고정 URL 표시/복사, ping·griddata 테스트 |
| 활동 및 검증 로그 | 시각, 작업, 실행자, 대상 계정, 결과, HTTP 상태, 처리 시간, 검사 단계, 50건 단위 조회, 결과 필터 |
| Admin Console | 전체 계정 조회, 대상 계정 콘솔 관리, 서비스·국가 정책 등록, 서비스 삭제, 전체 로그 조회 |

관리자는 대상 계정의 콘솔에서 VC 업로드·재검증·삭제, 세션 연결·초기화, 계약·해지, 키 재발급을 수행할 수 있습니다. 관리자도 VC 검증·국가 정책을 우회하지 않습니다. PoC에서는 서비스 정책 수정 대신 삭제·재등록합니다.

## 상태 간 관계

- **접속 키:** 계정당 1개. 재연결/초기화/VC 삭제에도 주소는 유지됩니다. 키 재발급 시에만 변경됩니다.
- **참여 세션:** 계정당 1개. 최대 24시간이며 VC·검증 결과 유효기간을 넘지 않습니다.
- **서비스 계약:** 계정 + 해당 세션 + 서비스에 연결. 만료는 세션·VC 기간 이내입니다.
- 세션 재연결 시 기존 계약을 해제합니다. 새 세션에서는 서비스를 다시 계약합니다.
- VC 세트 삭제 시 그 세트를 사용하는 세션과 계약을 해제합니다. 다른 세트는 유지됩니다.
- 초기화 시 세션과 계약만 해제합니다. VC·고정 키·활동 로그는 남습니다.
- 서비스 삭제 시 그 서비스의 모든 계약이 해제됩니다.
- 같은 회사 VC를 서로 다른 계정에 등록해도 계정별 계약과 데이터 접근은 분리됩니다.
- 접속 키는 만료되지 않습니다. **24시간 후 만료되는 것은 세션입니다.** 노출된 키는 재발급해야 합니다.

## 실제 Weather API 연결

외부 API 요청은 포털이 대행합니다. 별도 컨테이너는 필요 없습니다.

```bash
PORTAL_ADMIN_USERS=admin PORTAL_ALLOWED_DATA_ORIGINS=https://weather-api.bmap.kr python portal.py --port 8000
```

관리자가 서비스에 `https://weather-api.bmap.kr/api`와 같이 **API base URL**을 등록합니다. 소비자에게 표시되는 주소는 다음 형태입니다.

```text
https://gaia-x-portal.bmap.kr/access/{고정키}/{service_id}
```

| 소비자 요청 | 처리 |
|---|---|
| GET {base}/ping | 키·세션·VC·계약·국가 정책 점검 |
| GET {base}/griddata?source=... | Weather API base + /griddata에 쿼리 전달 |
| GET {base}/latest?... | Weather API base + /latest에 쿼리 전달 |

서비스 UUID를 경로에 사용합니다. 별도 slug 관리 기능은 추가하지 않았습니다. 허용 경로는 `ping`, `griddata`, `latest`입니다. 다른 Weather API 경로가 필요하면 allowlist를 명시적으로 확장해야 합니다.

외부 API는 리디렉션을 따르지 않고 인증 헤더를 전달하지 않습니다. 응답 최대 5MB, 타임아웃 30초입니다. 데이터는 크기 제한 내에서 메모리에 버퍼링한 뒤 반환합니다. 실제 API 주소·쿼리·응답 스펙과 Web-ECDIS의 연동은 별도로 확인해야 합니다. **샘플 JSON은 실제 격자 데이터 형식을 재현하지 않습니다.**

`/ping`, 연결, 계약은 전체 재검증합니다. 데이터 요청은 기존 검증기의 재검증 조건(60초/credentialStatus 등)을 그대로 유지합니다. 이번 변경에서는 캐시 정책을 완화하지 않았습니다.

## 서버 노출 설정

기본 허용 호스트에 `gaia-x-portal.bmap.kr`, `35.212.206.187`, localhost가 있습니다. 다른 호스트·브라우저 origin은 다음 환경변수로 지정합니다.

- `PORTAL_ALLOWED_HOSTS`: 쉼표 구분 호스트명 (스킴 제외)
- `PORTAL_ALLOWED_ORIGINS`: 쉼표 구분 브라우저 origin (스킴·포트 포함)
- `PORTAL_ALLOWED_DATA_ORIGINS`: 외부 데이터 API origin

외부 제공 시 HTTPS reverse proxy를 사용하세요. 앱은 TLS 인증서 설치나 DNS 설정을 수행하지 않습니다. URL의 키를 로그에 남기지 않도록 `python portal.py` 실행의 Uvicorn access log를 끕니다. 다른 방식으로 실행하면 `--no-access-log`를 지정하세요. Nginx 등 앞단에서도 `/access/` 경로의 access log를 끄거나 키를 마스킹해야 합니다.

PoC의 고정 주소 재표시를 위해 SQLite에 키 원문을 함께 저장합니다. DB 파일 접근을 제한하고 공유하지 마세요. 로그에는 비밀번호·원본 JWT·접속 키·쿼리·요청 본문을 기록하지 않습니다. 로그는 SQLite에 보관되며 변조 방지 감사 저장소는 아닙니다.

## 호환성 및 검증 범위

- 기존 SQLite 테이블에 필요한 컬럼/테이블을 자동 추가합니다. 업데이트 전 `data/`를 백업하세요.
- 기존 계정과 VC는 유지합니다. 계정/세션 귀속 정보가 없는 구버전 계약은 사용할 수 없으므로 재연결·재계약하세요.
- 루트 페이지는 새 `console.html`입니다. 기존 `dashboard.html`은 참고 파일로 보존하되 제공하지 않습니다.
- `/service-offerings` 등록은 이제 관리자 로그인 필수입니다. 기존 `X-Portal-Local`만으로 관리할 수 없습니다.
- 기존 `/demo-sessions`, `/negotiate`, `/transfer`는 유지하며 계약 소유권을 강화했습니다.
- VC 검증 모듈·정책·스키마 파일은 수정하지 않았습니다. 실제 EDC/DSP 계약, OID4VC, 공식 Gaia-X compliance 발급은 추가하지 않았습니다.

```bash
python -m unittest -v test_console
```

11개 통합 테스트: 성공 사이클/초기화/동일 URL 복구, 동일 VC를 쓴 계정 분리, VC 삭제, 키 재발급, 관리자 권한·국가 정책, 검사 실패 로그, 만료·해지·경로 제한, 잘못된 업로드, 관리자 이름 예약, 기존 엔드포인트 소유권, 외부 API 쿼리·응답 전달 및 인증 헤더 미전달 확인. 성공 VC 보고서는 테스트 fixture로 대체합니다. 실제 VC 서명 검증이나 실제 Weather API 연결을 완료했다는 의미는 아닙니다.

콘솔 DOM 동작 테스트도 수행했습니다: 관리자 로그인 → 서비스 등록 → 사용자 콘솔 열기 → VC 연결 → 계약 → ping/데이터 → 상세 로그 → 초기화 후 접근 거부. Chromium 다운로드 제한으로 실제 브라우저 렌더링의 시각 검사는 수행하지 못했습니다.
