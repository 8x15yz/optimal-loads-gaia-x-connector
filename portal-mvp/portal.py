"""Account-scoped FastAPI PoC console. External credentials are imported, never issued here."""
import argparse
import hashlib
import ipaddress
import json
import os
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from accounts import hash_password, valid_password, valid_username, verify_password
from credentials import MAX_TOTAL, PROFILE, date_value, inspect_set, read_uploads

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='BLUEMAP · Management Console PoC', version='0.5.0')
app.state.port = 8000
app.state.name = 'BLUEMAP Demo'
app.state.db = ROOT / 'data' / 'portal-8000.sqlite3'
app.state.resolver = None  # injection points for deterministic offline tests
app.state.resource_fetcher = None
app.state.verification_policy = None
# 서버에서 명시적으로 허용하는 호스트/브라우저 origin.
PUBLIC_HOSTS = {'35.212.206.187', 'gaia-x-portal.bmap.kr'} | {h.strip() for h in os.getenv('PORTAL_ALLOWED_HOSTS', '').split(',') if h.strip()}
ALLOWED_HOSTS = {'localhost', '127.0.0.1', 'testserver'} | PUBLIC_HOSTS
ORIGINS = {f'http://{h}:8000' for h in ({'localhost', '127.0.0.1'} | PUBLIC_HOSTS)}
ORIGINS |= {f'https://{h}' for h in PUBLIC_HOSTS}
ORIGINS |= {v.strip() for v in os.getenv('PORTAL_ALLOWED_ORIGINS', '').split(',') if v.strip()}
app.add_middleware(CORSMiddleware, allow_origins=sorted(ORIGINS), allow_methods=['GET', 'POST'],
                   allow_headers=['Authorization', 'Content-Type', 'X-Portal-Local'])

@app.middleware('http')
async def local_only(request: Request, call_next):
    from fastapi.responses import JSONResponse
    if request.url.hostname not in ALLOWED_HOSTS:
        return JSONResponse({'detail': '허용되지 않은 호스트입니다'}, status_code=403)
    origin = request.headers.get('origin')
    if origin and origin not in ORIGINS:
        return JSONResponse({'detail': '허용하지 않은 Origin'}, status_code=403)
    if request.method == 'POST':
        try:
            size = int(request.headers.get('content-length', '0'))
        except ValueError:
            return JSONResponse({'detail': '잘못된 Content-Length'}, status_code=400)
        if size > MAX_TOTAL + 100_000:
            return JSONResponse({'detail': '업로드 크기 제한 초과'}, status_code=413)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

@contextmanager
def db():
    path = Path(app.state.db)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, password_hash TEXT NOT NULL, created REAL);
    CREATE TABLE IF NOT EXISTS account_sessions(token_hash TEXT PRIMARY KEY, account_id TEXT, expires REAL);
    CREATE TABLE IF NOT EXISTS imports(id TEXT PRIMARY KEY, tokens TEXT, report TEXT, account_id TEXT, created REAL);
    CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, import_id TEXT, participant_id TEXT, expires REAL, account_id TEXT);
    CREATE TABLE IF NOT EXISTS services(id TEXT PRIMARY KEY, name TEXT, data_url TEXT, country TEXT);
    CREATE TABLE IF NOT EXISTS access_keys(account_id TEXT PRIMARY KEY, key_hash TEXT UNIQUE, key_value TEXT, created REAL);
    CREATE TABLE IF NOT EXISTS activity(id TEXT PRIMARY KEY, created REAL, actor_id TEXT, account_id TEXT, action TEXT, result TEXT, summary TEXT, duration_ms INTEGER, details TEXT);
    CREATE TABLE IF NOT EXISTS contracts(id TEXT PRIMARY KEY, participant_id TEXT, service_id TEXT, country TEXT, expires REAL);
    CREATE TABLE IF NOT EXISTS data_origins(origin TEXT PRIMARY KEY, note TEXT, created REAL, created_by TEXT);
    ''')
    # Migration for DB files created before accounts existed.
    for stmt in ('ALTER TABLE imports ADD COLUMN account_id TEXT',
                 'ALTER TABLE imports ADD COLUMN created REAL',
                 'ALTER TABLE sessions ADD COLUMN account_id TEXT',
                 'ALTER TABLE contracts ADD COLUMN account_id TEXT',
                 'ALTER TABLE contracts ADD COLUMN session_hash TEXT',
                 # 0.5: 참여자(participant) 단일 역할 + 운영자(operator) 분리
                 'ALTER TABLE accounts ADD COLUMN is_operator INTEGER NOT NULL DEFAULT 0',
                 'ALTER TABLE services ADD COLUMN owner_account_id TEXT',
                 'ALTER TABLE services ADD COLUMN provider_participant_id TEXT',
                 'ALTER TABLE services ADD COLUMN provider_import_id TEXT',
                 'ALTER TABLE services ADD COLUMN provider_name TEXT',
                 'ALTER TABLE services ADD COLUMN created REAL',
                 'ALTER TABLE contracts ADD COLUMN provider_participant_id TEXT'):
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError:
            pass
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def local_header(value):
    if value != '1':
        raise HTTPException(403, '로컬 포털 관리 요청 헤더가 필요합니다')

def inspect(tokens):
    try:
        options = {}
        if app.state.resolver: options['resolver'] = app.state.resolver
        if app.state.resource_fetcher: options['resource_fetcher'] = app.state.resource_fetcher
        if app.state.verification_policy: options['policy'] = app.state.verification_policy
        return inspect_set(tokens, **options)
    except Exception as e:
        raise HTTPException(400, '자격증명 입력 오류: ' + str(e)[:250])

def get_import(ident):
    with db() as c:
        row = c.execute('SELECT * FROM imports WHERE id=?', (ident,)).fetchone()
    if not row:
        raise HTTPException(404, '가져오기 기록이 없습니다')
    return row

def get_owned_import(ident, account_id):
    row = get_import(ident)
    if row['account_id'] != account_id:
        raise HTTPException(403, '본인 계정에 연결된 자격증명이 아닙니다')
    return row

def account_auth(authorization):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, '로그인이 필요합니다')
    token = authorization[7:]
    with db() as c:
        row = c.execute('SELECT * FROM account_sessions WHERE token_hash=?',
                         (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if not row or row['expires'] <= time.time():
        raise HTTPException(401, '로그인 세션이 없거나 만료되었습니다. 다시 로그인해주세요')
    audit_context(actor_id=row['account_id'], account_id=row['account_id'])
    return dict(row)

ACCOUNT_SESSION_TTL = 24 * 3600
# Constant reference used only to keep register/login timing similar whether
# or not the username exists; never a real account's credentials.
_DUMMY_SALT, _DUMMY_HASH = hash_password('not-a-real-account-password')

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)

@app.post('/accounts/register')
def register_account(req: RegisterRequest):
    reserved = {x.strip() for x in os.getenv('PORTAL_ADMIN_USERS','').split(',')} | {os.getenv('PORTAL_BOOTSTRAP_ADMIN_USER','admin')}
    if req.username in reserved:
        raise HTTPException(403, '관리자 계정은 서버에서 생성해야 합니다')
    if not valid_username(req.username):
        raise HTTPException(400, '아이디는 영문/숫자/._- 3~32자여야 합니다')
    if not valid_password(req.password):
        raise HTTPException(400, '비밀번호는 8~128자여야 합니다')
    salt, pw_hash = hash_password(req.password)
    ident = str(uuid.uuid4())
    try:
        with db() as c:
            c.execute('INSERT INTO accounts(id,username,salt,password_hash,created) VALUES (?,?,?,?,?)',
                      (ident, req.username, salt, pw_hash, time.time()))
    except sqlite3.IntegrityError:
        raise HTTPException(409, '이미 사용 중인 아이디입니다')
    audit_context(actor_id=ident, account_id=ident, summary='회원가입 완료')
    return {'account_id': ident, 'username': req.username}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post('/accounts/login')
def login_account(req: LoginRequest):
    with db() as c:
        row = c.execute('SELECT * FROM accounts WHERE username=?', (req.username,)).fetchone()
    salt, expected = (row['salt'], row['password_hash']) if row else (_DUMMY_SALT, _DUMMY_HASH)
    ok = verify_password(req.password, salt, expected)
    if not row or not ok:
        raise HTTPException(401, '아이디 또는 비밀번호가 올바르지 않습니다')
    token = secrets.token_urlsafe(32)
    expires = time.time() + ACCOUNT_SESSION_TTL
    with db() as c:
        c.execute('INSERT INTO account_sessions VALUES (?,?,?)',
                  (hashlib.sha256(token.encode()).hexdigest(), row['id'], expires))
    audit_context(actor_id=row['id'], account_id=row['id'], summary='로그인 완료')
    return {'access_token': token, 'account_id': row['id'], 'username': row['username'], 'expires_at': expires}

@app.post('/accounts/logout')
def logout_account(authorization: str = Header('')):
    if authorization.startswith('Bearer '):
        with db() as c:
            c.execute('DELETE FROM account_sessions WHERE token_hash=?',
                      (hashlib.sha256(authorization[7:].encode()).hexdigest(),))
    return {'status': 'ok'}

@app.get('/accounts/me')
def me(authorization: str = Header('')):
    acc = account_auth(authorization)
    with db() as c:
        row = c.execute('SELECT username FROM accounts WHERE id=?', (acc['account_id'],)).fetchone()
    return {'account_id': acc['account_id'], 'username': row['username'] if row else None,
            'is_operator': is_admin(acc['account_id'])}

@app.get('/accounts/me/credentials')
def my_credentials(authorization: str = Header('')):
    acc = account_auth(authorization)
    with db() as c:
        rows = c.execute('SELECT id, report, created FROM imports WHERE account_id=? ORDER BY created DESC',
                          (acc['account_id'],)).fetchall()
    out = []
    for r in rows:
        report = json.loads(r['report'])
        out.append({'id': r['id'], 'created': r['created'], 'summary': report['summary'],
                    'eligible_for_demo': report['eligible_for_demo'] and report.get('profile')==PROFILE,
                    'needs_recheck': report.get('profile')!=PROFILE})
    return {'credentials': out}

def authorize(authorization, fresh=False):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, '데모 세션 토큰이 필요합니다')
    token = authorization[7:]
    with db() as c:
        row = c.execute('SELECT * FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if not row or row['expires'] <= time.time():
        raise HTTPException(401, '세션이 없거나 만료되었습니다. 데모 참여자를 다시 연결해주세요')
    return validate_session(row, fresh)

def validate_session(row, fresh=False):
    audit_context(account_id=row['account_id'])
    if row['expires'] <= time.time():
        raise HTTPException(403, '참여 세션이 만료되었습니다')
    imported = get_import(row['import_id'])
    report = json.loads(imported['report'])
    try:
        age = time.time() - date_value(report.get('verified_at')).timestamp()
    except (ValueError, TypeError):
        age = float('inf')
    if fresh or report.get('profile')!=PROFILE or report.get('has_credential_status') or age<0 or age>=60:
        report = inspect(json.loads(imported['tokens']))
        audit_report(report)
        with db() as c:
            c.execute('UPDATE imports SET report=? WHERE id=?',(json.dumps(report),imported['id']))
    if not report['eligible_for_demo']:
        raise HTTPException(403, '현재 자격증명 검증에 실패했거나 확인 불가입니다. 가져오기 화면에서 재검증해주세요')
    # Even a catalog call must not accept credentials after their VC dates expire.
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if not report.get('valid_until') or now >= date_value(report['valid_until']):
        raise HTTPException(403, '자격증명·인증서·상태 목록의 유효기간이 지났습니다')
    for d in report['documents']:
        if not date_value(d['payload']['validFrom']) <= now < date_value(d['payload']['validUntil']):
            raise HTTPException(403, '자격증명 유효기간이 지났습니다')
    return dict(row), report

@app.get('/')
def ui():
    return FileResponse(ROOT / 'console.html')

@app.get('/health')
def health():
    return {'status': 'ok', 'name': app.state.name, 'port': app.state.port, 'mode': 'non-production demo', 'profile': PROFILE}

@app.get('/participant')
def participant():
    return {'name': app.state.name}

@app.post('/credentials/import')
async def import_credentials(files: list[UploadFile] = File(...), x_portal_local: str = Header(''),
                              authorization: str = Header(''), account_id: str | None = None):
    acc = {'account_id': target_account(authorization, account_id)}
    if not 1 <= len(files) <= 20:
        raise HTTPException(400, '파일 1~20개를 선택해주세요')
    inputs, total = [], 0
    for f in files:
        data = await f.read(MAX_TOTAL + 1)
        total += len(data)
        if total > MAX_TOTAL:
            raise HTTPException(413, '전체 업로드는 8 MB 이하여야 합니다')
        inputs.append((f.filename or '', data))
    try:
        tokens = read_uploads(inputs)
    except Exception as e:
        raise HTTPException(400, str(e)[:200])
    # Run network and crypto work outside the async event loop.
    from starlette.concurrency import run_in_threadpool
    report = await run_in_threadpool(inspect, tokens)
    audit_report(report)
    ident = str(uuid.uuid4())
    with db() as c:
        c.execute('INSERT INTO imports VALUES (?,?,?,?,?)',
                  (ident, json.dumps(tokens), json.dumps(report), acc['account_id'], time.time()))
    return {'id': ident, 'report': report}

class Recheck(BaseModel):
    import_id: str

@app.post('/credentials/recheck')
def recheck(req: Recheck, x_portal_local: str = Header(''), authorization: str = Header('')):
    acc = account_auth(authorization)
    record = get_owned_import(req.import_id, acc['account_id'])
    report = inspect(json.loads(record['tokens']))
    audit_report(report)
    with db() as c:
        c.execute('UPDATE imports SET report=? WHERE id=?', (json.dumps(report), req.import_id))
    return {'id': req.import_id, 'report': report}

@app.post('/demo-sessions')
def activate(req: Recheck, x_portal_local: str = Header(''), authorization: str = Header('')):
    acc = account_auth(authorization)
    imported = get_owned_import(req.import_id, acc['account_id'])
    report = inspect(json.loads(imported['tokens']))
    audit_report(report)
    if not report['eligible_for_demo']:
        raise HTTPException(403, '서명·발급자·기간·세트 연결 검증을 통과해야 연결할 수 있습니다')
    token = secrets.token_urlsafe(32)
    subject = report['summary']['subject_id']
    # This is explicitly a local demo mapping, not proof of the uploader's legal identity.
    pid = participant_id_for(subject)
    expires = min(time.time() + 24 * 3600, date_value(report['valid_until']).timestamp())
    with db() as c:
        c.execute('DELETE FROM contracts WHERE account_id=?', (acc['account_id'],))
        c.execute('DELETE FROM sessions WHERE account_id=?', (acc['account_id'],))
        ensure_key(c, acc['account_id'])
        c.execute('INSERT INTO sessions VALUES (?,?,?,?,?)',
                  (hashlib.sha256(token.encode()).hexdigest(), req.import_id, pid, expires, acc['account_id']))
        c.execute('UPDATE imports SET report=? WHERE id=?', (json.dumps(report), req.import_id))
    return {'access_token': token, 'participant_id': pid, 'expires_at': expires, 'summary': report['summary'],
            'notice': '로컬 데모 연결입니다. 업로더의 회사 대표 권한은 증명하지 않습니다.'}

class ServiceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    data_url: str = Field(default='demo://weather', max_length=2048)
    country: str = Field(default='KR', pattern=r'^[A-Z]{2}$')
    # 운영자가 대상 참여자 콘솔에서 대신 등록할 때만 사용
    account_id: str | None = None
    # 운영자 전용: 참여자가 아닌 플랫폼 연결 테스트용 샘플(demo://weather만 허용)
    platform_sample: bool = False

# ---- 데이터 API origin 허용 목록(allowlist) ----
# 서버 환경변수(PORTAL_ALLOWED_DATA_ORIGINS) + 운영자 콘솔 등록분(data_origins 테이블)의 합집합.
# 환경변수 항목은 재배포 없이 바꿀 수 없는 기준선, 콘솔 항목은 운영자가 즉시 추가·해제.
DEFAULT_PORTS = {'http': 80, 'https': 443}

def origin_of(url, origin_only=False):
    """URL에서 정규화된 origin(scheme://host[:port]) 추출. 형식 오류 시 ValueError.

    scheme·host 소문자화, 기본 포트 제거, 계정정보 금지.
    origin_only=True면 경로·쿼리·프래그먼트가 붙은 입력도 거부.
    """
    parsed = urlsplit((url or '').strip())
    scheme = parsed.scheme.lower()
    if scheme not in DEFAULT_PORTS:
        raise ValueError('http 또는 https만 허용합니다')
    if parsed.username or parsed.password:
        raise ValueError('계정정보가 포함된 주소는 허용하지 않습니다')
    host = (parsed.hostname or '').lower()
    if not host:
        raise ValueError('호스트가 없습니다')
    try:
        port = parsed.port
    except ValueError:
        raise ValueError('포트 형식이 올바르지 않습니다')
    if origin_only and (parsed.path not in ('', '/') or parsed.query or parsed.fragment):
        raise ValueError('경로·쿼리 없이 origin만 입력하세요 (예: https://weather-api.example.com)')
    shown = f'[{host}]' if ':' in host else host
    return f'{scheme}://{shown}' + (f':{port}' if port and port != DEFAULT_PORTS[scheme] else '')

def reject_internal_host(origin):
    """콘솔 등록 시 내부망·메타데이터 주소 차단. IP 리터럴과 대표적인 내부 호스트명만 검사.

    도메인이 내부 IP로 해석되는 경우(DNS rebinding 등)까지 막지는 못함.
    """
    host = urlsplit(origin).hostname or ''
    if host == 'localhost' or host.endswith(('.localhost', '.internal', '.local')):
        raise ValueError('내부 호스트명은 콘솔에서 허용할 수 없습니다')
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return
    if not ip.is_global:
        raise ValueError('사설·루프백·링크로컬 등 공인 인터넷이 아닌 IP는 콘솔에서 허용할 수 없습니다')

def env_data_origins():
    out = set()
    for v in os.getenv('PORTAL_ALLOWED_DATA_ORIGINS', '').split(','):
        if v.strip():
            try:
                out.add(origin_of(v, origin_only=True))
            except ValueError:
                pass  # 잘못된 서버 설정 항목은 무시(허용하지 않음)
    return out

def allowed_data_origins():
    with db() as c:
        return env_data_origins() | {r['origin'] for r in c.execute('SELECT origin FROM data_origins')}

def validate_data_url(url):
    if url == 'demo://weather':
        return
    try:
        origin = origin_of(url)
    except ValueError as e:
        raise HTTPException(400, f'데이터 API 주소 오류: {e}')
    if origin not in allowed_data_origins():
        raise HTTPException(400, f'{origin} 은(는) 데이터 API 허용 목록에 없습니다. 운영자에게 origin 허용을 요청하세요')

def participant_id_for(subject):
    # 로컬 데모 매핑. 업로더의 법적 대표 권한을 증명하지 않음.
    return 'demo:' + hashlib.sha256(subject.encode()).hexdigest()[:24]

def provider_status(service):
    """제공자 쪽 상태 점검. (ok, reason) 반환.

    참여자가 등록한 서비스는 등록에 사용한 VC 세트가 남아 있고, 최근 검증 결과가
    통과이며, 유효기간 이내일 때만 제공 중으로 봅니다. 제공자의 24시간 세션과는
    분리해서 세션 만료·초기화만으로 서비스가 사라지지 않게 합니다.
    """
    if service['data_url'] != 'demo://weather':
        try:
            allowed = origin_of(service['data_url']) in allowed_data_origins()
        except ValueError:
            allowed = False
        if not allowed:
            return False, '운영자가 이 데이터 API origin의 허용을 해제해 제공이 중지되었습니다'
    if not service['owner_account_id']:
        return True, None  # 운영자 샘플 또는 0.4 이전 서비스
    with db() as c:
        row = c.execute('SELECT report FROM imports WHERE id=? AND account_id=?',
                        (service['provider_import_id'], service['owner_account_id'])).fetchone()
    if not row:
        return False, '제공자가 등록에 사용한 VC를 삭제해 제공이 중지되었습니다'
    report = json.loads(row['report'])
    if report.get('profile') != PROFILE or not report.get('eligible_for_demo'):
        return False, '제공자 VC가 최근 검증을 통과하지 못해 제공이 중지되었습니다'
    from datetime import datetime, timezone
    try:
        if datetime.now(timezone.utc) >= date_value(report['valid_until']):
            return False, '제공자 자격증명 유효기간이 지나 제공이 중지되었습니다'
    except (KeyError, ValueError, TypeError):
        return False, '제공자 자격증명 유효기간을 확인할 수 없습니다'
    return True, None

def require_provider_active(service):
    ok, reason = provider_status(service)
    if not ok:
        raise HTTPException(403, reason)

def public_service(row, viewer_account_id, operator=False):
    ok, reason = provider_status(row)
    mine = bool(row['owner_account_id']) and row['owner_account_id'] == viewer_account_id
    out = {'id': row['id'], 'name': row['name'], 'country': row['country'],
           'provider_name': row['provider_name'] or app.state.name,
           'provider_participant_id': row['provider_participant_id'],
           'platform_sample': not row['owner_account_id'], 'sample': row['data_url'] == 'demo://weather',
           'mine': mine, 'active': ok, 'status_reason': reason, 'created': row['created']}
    # 다른 참여자의 원본 API 주소는 제공자 본인과 운영자에게만 노출
    if mine or operator:
        out['data_url'] = row['data_url']
    return out

@app.post('/service-offerings')
def register(req: ServiceRequest, x_portal_local: str = Header(''), authorization: str = Header('')):
    me = account_auth(authorization)['account_id']
    validate_data_url(req.data_url)
    if req.platform_sample:
        if not is_admin(me):
            raise HTTPException(403, '플랫폼 샘플 서비스는 운영자만 등록할 수 있습니다')
        if req.data_url != 'demo://weather':
            raise HTTPException(400, '실제 API는 VC를 연결한 참여자로 등록해야 합니다. 플랫폼 샘플은 demo://weather만 허용합니다')
        owner = pid = import_id = None
        provider_name = f'{app.state.name} · 플랫폼 샘플'
    else:
        owner = target_account(authorization, req.account_id)
        with db() as c:
            has_session = c.execute('SELECT 1 FROM sessions WHERE account_id=? AND expires>?', (owner, time.time())).fetchone()
        if not has_session:
            raise HTTPException(403, '서비스 제공은 VC 검증을 통과해 참여 세션을 연결한 참여자만 할 수 있습니다')
        session, report = active_session(owner, fresh=True)
        pid, import_id = session['participant_id'], session['import_id']
        summary = report.get('summary', {})
        provider_name = summary.get('legal_name') or summary.get('name') or pid
    ident = str(uuid.uuid4())
    with db() as c:
        c.execute('INSERT INTO services(id,name,data_url,country,owner_account_id,provider_participant_id,provider_import_id,provider_name,created) '
                  'VALUES (?,?,?,?,?,?,?,?,?)',
                  (ident, req.name, req.data_url, req.country, owner, pid, import_id, provider_name, time.time()))
    audit_context(summary='서비스 오퍼링 등록' + (' (플랫폼 샘플)' if req.platform_sample else ''))
    return {'service_offering_id': ident, 'provider_participant_id': pid, 'platform_sample': req.platform_sample}

@app.get('/service-offerings')
def services(x_portal_local: str = Header(''), authorization: str = Header('')):
    me = account_auth(authorization)['account_id']
    operator = is_admin(me)
    with db() as c:
        rows = c.execute('SELECT * FROM services ORDER BY created').fetchall()
    return {'services': [public_service(r, me, operator) for r in rows]}

@app.post('/service-offerings/{service_id}/delete')
def delete_own_service(service_id: str, authorization: str = Header('')):
    me = account_auth(authorization)['account_id']
    with db() as c:
        row = c.execute('SELECT owner_account_id FROM services WHERE id=?', (service_id,)).fetchone()
    if not row:
        raise HTTPException(404, '서비스가 없습니다')
    if row['owner_account_id'] != me and not is_admin(me):
        raise HTTPException(403, '본인이 제공하는 서비스만 삭제할 수 있습니다')
    with db() as c:
        c.execute('DELETE FROM contracts WHERE service_id=?', (service_id,))
        c.execute('DELETE FROM services WHERE id=?', (service_id,))
    audit_context(summary='서비스 오퍼링 삭제')
    return {'status': 'ok'}

@app.get('/catalog')
def catalog(authorization: str = Header('')):
    session, _ = authorize(authorization)
    with db() as c:
        rows = c.execute('SELECT * FROM services ORDER BY created').fetchall()
    offerings = []
    for r in rows:
        item = public_service(r, session['account_id'])
        if item['active']:
            offerings.append({k: item[k] for k in ('id', 'name', 'country', 'provider_name', 'provider_participant_id', 'platform_sample', 'mine')})
    return {'participant': app.state.name, 'service_offerings': offerings}

class NegotiateRequest(BaseModel):
    service_offering_id: str

@app.post('/negotiate')
def negotiate(req: NegotiateRequest, authorization: str = Header('')):
    session, report = authorize(authorization, fresh=True)
    return create_contract(session, report, req.service_offering_id)

def create_contract(session, report, service_id):
    with db() as c:
        service = c.execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
        if not service:
            raise HTTPException(404, '서비스가 없습니다')
        if service['owner_account_id'] == session['account_id'] or (
                service['provider_participant_id'] and service['provider_participant_id'] == session['participant_id']):
            raise HTTPException(403, '자신이 제공하는 서비스는 계약할 수 없습니다')
        require_provider_active(service)
        if service['country'] != report['summary']['country']:
            raise HTTPException(403, f"국가 정책 불일치: 요청자 {report['summary']['country']} / 정책 {service['country']}")
        ident = str(uuid.uuid4())
        expires = min(session['expires'], date_value(report['valid_until']).timestamp())
        c.execute('DELETE FROM contracts WHERE account_id=? AND service_id=?', (session['account_id'], service['id']))
        c.execute('INSERT INTO contracts(id,participant_id,service_id,country,expires,account_id,session_hash,provider_participant_id) VALUES (?,?,?,?,?,?,?,?)',
                  (ident, session['participant_id'], service['id'], service['country'], expires, session['account_id'], session['token_hash'], service['provider_participant_id']))
    return {'contract_id': ident, 'expires_at': expires, 'participant_id': session['participant_id'],
            'consumer_participant_id': session['participant_id'], 'provider_participant_id': service['provider_participant_id'],
            'mode': 'demo-access-grant', 'notice': '세션 만료 시각 이내의 데모 접근 승인입니다. 양측 서명 DAC/DUA는 아직 구현하지 않았습니다.'}

class TransferRequest(BaseModel):
    contract_id: str

@app.post('/transfer')
def transfer(req: TransferRequest, authorization: str = Header('')):
    session, report = authorize(authorization, fresh=True)
    with db() as c:
        contract = c.execute('SELECT * FROM contracts WHERE id=?', (req.contract_id,)).fetchone()
        if not contract or contract['account_id'] != session['account_id'] or contract['session_hash'] != session['token_hash']:
            raise HTTPException(403, '접근 승인 대상과 인증된 요청자가 일치하지 않습니다')
        if contract['expires'] <= time.time():
            raise HTTPException(403, '접근 승인이 만료되었습니다')
        service = c.execute('SELECT * FROM services WHERE id=?', (contract['service_id'],)).fetchone()
    if not service or service['country'] != report['summary']['country']:
        raise HTTPException(403, '현재 서비스 정책에 맞지 않습니다')
    require_provider_active(service)
    validate_data_url(service['data_url'])
    if service['data_url'] == 'demo://weather':
        data = {'sample': True, 'location': 'Busan', 'temperature_c': 24, 'wind_speed_ms': 5.2,
                'notice': '연결 테스트용 고정 샘플이며 실제 기상 관측값이 아닙니다.'}
    else:
        try:
            with httpx.Client(timeout=15, follow_redirects=False) as client:
                with client.stream('GET', service['data_url']) as r:
                    r.raise_for_status()
                    body = b''
                    for chunk in r.iter_bytes():
                        body += chunk
                        if len(body) > 5_000_000:
                            raise ValueError('데이터 응답은 5 MB 이하여야 합니다')
                    data = json.loads(body)
        except Exception as e:
            raise HTTPException(502, '데이터 API 호출 실패: ' + type(e).__name__)
    return {'status': 'transferred', 'service': service['name'], 'data': data}


# PoC console: account-owned state and an append-only activity history.
AUDIT = ContextVar('audit', default=None)

def audit_context(**values):
    event = AUDIT.get()
    if event is not None:
        event.update(values)

def audit_report(report):
    event = AUDIT.get()
    if event is not None:
        event.setdefault('details', {})['checks'] = report.get('checks', [])
        event['result'] = 'pass' if report.get('eligible_for_demo') else 'fail'
        event['summary'] = 'VC 검증 통과' if report.get('eligible_for_demo') else 'VC 검증: 차단 항목 확인 필요'

@app.exception_handler(HTTPException)
async def audited_error(request, exc):
    audit_context(summary=str(exc.detail), result='fail')
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code, headers=exc.headers)

@app.middleware('http')
async def activity_log(request: Request, call_next):
    # Never log bearer keys, raw JWTs, passwords, request bodies or query strings.
    path = request.url.path
    action = '/access/{key}/' + '/'.join(path.split('/')[3:]) if path.startswith('/access/') else path
    tracked = request.method == 'POST' or path.startswith('/access/')
    event = {'action': request.method + ' ' + action, 'details': {}}
    marker = AUDIT.set(event)
    started = time.monotonic()
    try:
        response = await call_next(request)
        if tracked:
            result = event.get('result', 'pass' if response.status_code < 400 else 'fail')
            if response.status_code >= 400: result = 'fail'
            details = event['details']
            details['http_status'] = response.status_code
            ident = str(uuid.uuid4())
            with db() as c:
                c.execute('INSERT INTO activity VALUES (?,?,?,?,?,?,?,?,?)',
                    (ident, time.time(), event.get('actor_id'), event.get('account_id'), event['action'], result,
                     event.get('summary', '처리 완료' if result == 'pass' else '요청 실패'),
                     round((time.monotonic()-started)*1000), json.dumps(details, ensure_ascii=False)))
            response.headers['X-Activity-ID'] = ident
        return response
    finally:
        AUDIT.reset(marker)

def is_admin(account_id):
    """운영자(operator) 여부. 참여자 역할과 무관한 플랫폼 관리 권한.

    manage_admin.py가 DB에 기록한 is_operator 플래그가 기준이며, 0.4 호환을 위해
    PORTAL_ADMIN_USERS 환경변수에 지정된 이름도 운영자로 인정합니다.
    가입 순서나 아이디 이름으로는 권한이 생기지 않습니다.
    """
    with db() as c:
        row = c.execute('SELECT username, is_operator FROM accounts WHERE id=?', (account_id,)).fetchone()
    if not row:
        return False
    legacy = {x.strip() for x in os.getenv('PORTAL_ADMIN_USERS', '').split(',') if x.strip()}
    return bool(row['is_operator']) or row['username'] in legacy

is_operator = is_admin

def require_admin(authorization):
    acc = account_auth(authorization)
    if not is_admin(acc['account_id']):
        raise HTTPException(403, '관리자 권한이 필요합니다')
    return acc

def target_account(authorization, account_id=None):
    acc = account_auth(authorization)
    target = account_id or acc['account_id']
    if target != acc['account_id'] and not is_admin(acc['account_id']):
        raise HTTPException(403, '본인 계정만 관리할 수 있습니다')
    with db() as c:
        if not c.execute('SELECT id FROM accounts WHERE id=?', (target,)).fetchone():
            raise HTTPException(404, '계정이 없습니다')
    audit_context(account_id=target)
    return target

def ensure_key(c, account_id, rotate=False):
    row = c.execute('SELECT key_value FROM access_keys WHERE account_id=?', (account_id,)).fetchone()
    if row and not rotate: return row['key_value']
    key = secrets.token_urlsafe(32)
    c.execute('INSERT OR REPLACE INTO access_keys VALUES (?,?,?,?)',
              (account_id, hashlib.sha256(key.encode()).hexdigest(), key, time.time()))
    return key

def active_session(account_id, fresh=False):
    with db() as c:
        row = c.execute('SELECT * FROM sessions WHERE account_id=? ORDER BY expires DESC LIMIT 1', (account_id,)).fetchone()
    if not row: raise HTTPException(403, '연결된 참여 세션이 없습니다')
    return validate_session(row, fresh)

def checked_contract(session, report, service_id):
    with db() as c:
        contract = c.execute('SELECT * FROM contracts WHERE account_id=? AND session_hash=? AND service_id=? AND expires>?',
            (session['account_id'], session['token_hash'], service_id, time.time())).fetchone()
        service = c.execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
    if not contract: raise HTTPException(403, '활성 서비스 계약이 없습니다. 카탈로그에서 계약해주세요')
    if not service or service['country'] != report['summary']['country']:
        raise HTTPException(403, '서비스 국가 정책 불일치')
    require_provider_active(service)
    return dict(contract), dict(service)

@app.get('/console/state')
def console_state(authorization: str = Header(''), account_id: str | None = None):
    target = target_account(authorization, account_id)
    me = account_auth(authorization)['account_id']
    with db() as c:
        user = dict(c.execute('SELECT id,username,created FROM accounts WHERE id=?', (target,)).fetchone())
        imports = []
        for r in c.execute('SELECT id,created,report FROM imports WHERE account_id=? ORDER BY created DESC', (target,)):
            report = json.loads(r['report'])
            imports.append({'id':r['id'],'created':r['created'],'summary':report.get('summary',{}),
                            'eligible':report.get('eligible_for_demo',False),'valid_until':report.get('valid_until'),
                            'checks':report.get('checks',[])})
        sessions = [dict(r) for r in c.execute('SELECT import_id,participant_id,expires FROM sessions WHERE account_id=?', (target,))]
        contracts = [dict(r) for r in c.execute('SELECT id,service_id,expires FROM contracts WHERE account_id=?', (target,))]
        service_rows = c.execute('SELECT * FROM services ORDER BY created').fetchall()
        key = c.execute('SELECT key_value FROM access_keys WHERE account_id=?', (target,)).fetchone()
        active = c.execute('SELECT s.participant_id, i.report FROM sessions s JOIN imports i ON i.id=s.import_id '
                           'WHERE s.account_id=? AND s.expires>? ORDER BY s.expires DESC LIMIT 1', (target, time.time())).fetchone()
        provided = []
        for r in c.execute('SELECT c.id, c.service_id, c.participant_id, c.expires, c.session_hash, s.name AS service_name '
                           'FROM contracts c JOIN services s ON s.id=c.service_id WHERE s.owner_account_id=? ORDER BY c.expires DESC', (target,)):
            consumer = c.execute('SELECT i.report FROM sessions se JOIN imports i ON i.id=se.import_id WHERE se.token_hash=?',
                                 (r['session_hash'],)).fetchone()
            name = json.loads(consumer['report']).get('summary', {}).get('legal_name') if consumer else None
            provided.append({'id': r['id'], 'service_id': r['service_id'], 'service_name': r['service_name'],
                             'consumer_participant_id': r['participant_id'], 'consumer_name': name, 'expires': r['expires']})
    operator = is_admin(me)
    participant = None
    if active:
        summary = json.loads(active['report']).get('summary', {})
        participant = {'participant_id': active['participant_id'], 'legal_name': summary.get('legal_name'), 'country': summary.get('country')}
    return {'user':user,'is_operator':operator,'is_admin':operator,'target_is_operator':is_admin(target),
            'participant':participant,'credentials':imports,'sessions':sessions,'contracts':contracts,
            'services':[public_service(r, target, operator) for r in service_rows],'provided_contracts':provided,
            'data_origins':sorted(allowed_data_origins()),
            'access_path': '/access/'+key['key_value'] if key else None,'now':time.time()}

class ConsoleAction(BaseModel):
    account_id: str | None = None
    import_id: str | None = None
    service_id: str | None = None

@app.post('/console/{action}')
def console_action(action: str, req: ConsoleAction, authorization: str = Header('')):
    target = target_account(authorization, req.account_id)
    audit_context(action=action, summary={'connect':'참여 세션 연결 (최대 24시간)', 'reset':'세션·계약 초기화 (접속 주소 유지)',
        'delete-vc':'VC 삭제 및 연결된 세션·계약 해제', 'recheck':'VC 재검증', 'rotate-key':'접속 키 재발급',
        'contract':'서비스 계약', 'revoke-contract':'서비스 계약 해지'}.get(action, action))
    if action in {'delete-vc','recheck','connect'}:
        if not req.import_id: raise HTTPException(400, 'VC 세트를 선택해주세요')
        record = get_owned_import(req.import_id, target)
    if action in {'recheck','connect'}:
        report = inspect(json.loads(record['tokens']))
        audit_report(report)
        with db() as c:
            c.execute('UPDATE imports SET report=? WHERE id=?', (json.dumps(report),req.import_id))
        if action == 'recheck': return {'report':report}
        if not report['eligible_for_demo']: raise HTTPException(403, 'VC 검증을 통과해야 세션을 연결할 수 있습니다')
        expires = min(time.time()+24*3600, date_value(report['valid_until']).timestamp())
        if expires <= time.time(): raise HTTPException(403, 'VC 유효기간이 지났습니다')
        pid = participant_id_for(report['summary']['subject_id'])
        with db() as c:
            c.execute('DELETE FROM contracts WHERE account_id=?', (target,))
            c.execute('DELETE FROM sessions WHERE account_id=?', (target,))
            c.execute('INSERT INTO sessions VALUES (?,?,?,?,?)', (hashlib.sha256(secrets.token_bytes(32)).hexdigest(),req.import_id,pid,expires,target))
            ensure_key(c,target)
        return {'expires_at':expires,'participant_id':pid}
    if action == 'contract':
        session, report = active_session(target, fresh=True)
        return create_contract(session, report, req.service_id)
    with db() as c:
        if action == 'reset':
            c.execute('DELETE FROM contracts WHERE account_id=?', (target,))
            c.execute('DELETE FROM sessions WHERE account_id=?', (target,))
        elif action == 'delete-vc':
            c.execute('DELETE FROM contracts WHERE account_id=? AND session_hash IN (SELECT token_hash FROM sessions WHERE import_id=?)', (target,req.import_id))
            c.execute('DELETE FROM sessions WHERE account_id=? AND import_id=?', (target,req.import_id))
            c.execute('DELETE FROM imports WHERE id=? AND account_id=?', (req.import_id,target))
        elif action == 'rotate-key': ensure_key(c,target,rotate=True)
        elif action == 'revoke-contract': c.execute('DELETE FROM contracts WHERE account_id=? AND service_id=?', (target,req.service_id))
        else: raise HTTPException(404,'지원하지 않는 작업')
    return {'status':'ok'}

@app.get('/console/logs')
def console_logs(authorization: str = Header(''), account_id: str | None = None,
                 all_accounts: bool = False, result: str = '', offset: int = 0):
    acc = account_auth(authorization)
    if all_accounts:
        require_admin(authorization)
        where, params = '1=1', []
    else:
        target = target_account(authorization,account_id)
        where, params = 'a.account_id=?', [target]
    if result:
        where += ' AND a.result=?'; params.append(result)
    offset=max(0,offset)
    with db() as c:
        total=c.execute('SELECT COUNT(*) FROM activity a WHERE '+where,params).fetchone()[0]
        rows=c.execute('SELECT a.*, u.username, actor.username AS actor_username FROM activity a LEFT JOIN accounts u ON u.id=a.account_id LEFT JOIN accounts actor ON actor.id=a.actor_id WHERE '+where+' ORDER BY a.created DESC LIMIT 50 OFFSET ?',params+[offset]).fetchall()
    return {'total':total,'logs':[{**dict(r),'details':json.loads(r['details'])} for r in rows]}

class OriginRequest(BaseModel):
    origin: str = Field(min_length=1, max_length=300)
    note: str = Field(default='', max_length=200)

@app.get('/admin/data-origins')
def list_data_origins(authorization: str = Header('')):
    require_admin(authorization)
    env = env_data_origins()
    with db() as c:
        rows = [dict(r) for r in c.execute('SELECT d.origin, d.note, d.created, a.username AS created_by FROM data_origins d '
                                           'LEFT JOIN accounts a ON a.id=d.created_by ORDER BY d.created DESC')]
        urls = [r['data_url'] for r in c.execute("SELECT data_url FROM services WHERE data_url!='demo://weather'")]
    usage = {}
    for u in urls:
        try:
            o = origin_of(u); usage[o] = usage.get(o, 0) + 1
        except ValueError:
            pass
    items = [{**r, 'source': 'console', 'deletable': r['origin'] not in env, 'services': usage.get(r['origin'], 0)} for r in rows]
    known = {r['origin'] for r in rows}
    items += [{'origin': o, 'note': '서버 환경변수 PORTAL_ALLOWED_DATA_ORIGINS', 'created': None, 'created_by': None,
               'source': 'server', 'deletable': False, 'services': usage.get(o, 0)} for o in sorted(env - known)]
    return {'origins': items}

@app.post('/admin/data-origins')
def add_data_origin(req: OriginRequest, authorization: str = Header('')):
    me = require_admin(authorization)['account_id']
    try:
        origin = origin_of(req.origin, origin_only=True)
        reject_internal_host(origin)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if origin in env_data_origins():
        raise HTTPException(409, '이미 서버 설정으로 허용된 origin입니다')
    try:
        with db() as c:
            c.execute('INSERT INTO data_origins VALUES (?,?,?,?)', (origin, req.note.strip(), time.time(), me))
    except sqlite3.IntegrityError:
        raise HTTPException(409, '이미 허용된 origin입니다')
    audit_context(summary=f'데이터 API origin 허용: {origin}')
    return {'origin': origin}

@app.post('/admin/data-origins/delete')
def delete_data_origin(req: OriginRequest, authorization: str = Header('')):
    require_admin(authorization)
    try:
        origin = origin_of(req.origin, origin_only=True)
    except ValueError as e:
        raise HTTPException(400, str(e))
    with db() as c:
        deleted = c.execute('DELETE FROM data_origins WHERE origin=?', (origin,)).rowcount
    if not deleted:
        if origin in env_data_origins():
            raise HTTPException(400, '서버 환경변수로 허용된 origin은 콘솔에서 해제할 수 없습니다')
        raise HTTPException(404, '허용 목록에 없는 origin입니다')
    audit_context(summary=f'데이터 API origin 허용 해제: {origin}')
    return {'status': 'ok', 'origin': origin, 'still_allowed_by_server': origin in env_data_origins()}

@app.get('/admin/accounts')
def admin_accounts(authorization: str = Header('')):
    require_admin(authorization)
    with db() as c:
        rows=[dict(r) for r in c.execute('SELECT id,username,created FROM accounts ORDER BY created DESC')]
    return {'accounts':[{**r,'is_operator':is_admin(r['id'])} for r in rows]}

@app.post('/admin/services/{service_id}/delete')
def delete_service(service_id: str, authorization: str = Header('')):
    require_admin(authorization)
    return delete_own_service(service_id, authorization)

@app.get('/access/{key}/{service_id}/{path}')
def fixed_access(key: str, service_id: str, path: str, request: Request):
    if path not in {'ping','griddata','latest'}: raise HTTPException(404,'허용되지 않은 데이터 경로')
    with db() as c:
        row=c.execute('SELECT account_id FROM access_keys WHERE key_hash=?',(hashlib.sha256(key.encode()).hexdigest(),)).fetchone()
    if not row: raise HTTPException(403,'접속 키가 없거나 폐기되었습니다')
    audit_context(account_id=row['account_id'])
    session,report=active_session(row['account_id'],fresh=path=='ping')
    contract,service=checked_contract(session,report,service_id)
    audit_context(details={**AUDIT.get().get('details',{}),'stages':[
        {'name':'접속 키','status':'pass'},{'name':'참여 세션 / VC 유효성','status':'pass'},
        {'name':'서비스 계약 / 국가 정책','status':'pass'}]})
    if path=='ping': return {'status':'ready','participant_id':session['participant_id'],'expires_at':min(session['expires'],contract['expires'])}
    validate_data_url(service['data_url'])
    if service['data_url']=='demo://weather':
        return {'sample':True,'location':'Busan','temperature_c':24,'wind_speed_ms':5.2,'notice':'PoC 고정 샘플. 실제 기상/격자 API 응답 형식은 아닙니다.'}
    base=urlsplit(service['data_url'])
    if base.query or base.fragment: raise HTTPException(400,'서비스에는 쿼리 없는 API base URL을 등록해주세요')
    try:
        with httpx.Client(timeout=30,follow_redirects=False) as client:
            with client.stream('GET',service['data_url'].rstrip('/')+'/'+path,params=request.query_params.multi_items()) as r:
                if not 200<=r.status_code<300: raise ValueError('provider rejected')
                chunks=[]; size=0
                for chunk in r.iter_bytes():
                    size+=len(chunk)
                    if size>5_000_000: raise ValueError('response too large')
                    chunks.append(chunk)
                return Response(b''.join(chunks),status_code=r.status_code,media_type=r.headers.get('content-type','application/octet-stream'),headers={'Content-Disposition':'attachment'})
    except (httpx.HTTPError,ValueError):
        raise HTTPException(502,'Weather API 호출 실패 또는 응답 크기 제한 초과')

# Provision admin locally, before serving. Passwords are never embedded in source.
def bootstrap_admin(username, password):
    if not valid_username(username) or not valid_password(password):
        raise ValueError('관리자 아이디 3~32자, 비밀번호 8~128자 필요')
    salt,pw_hash=hash_password(password)
    with db() as c:
        row=c.execute('SELECT id FROM accounts WHERE username=?',(username,)).fetchone()
        if row:
            c.execute('UPDATE accounts SET salt=?,password_hash=?,is_operator=1 WHERE id=?',(salt,pw_hash,row['id']))
            c.execute('DELETE FROM account_sessions WHERE account_id=?',(row['id'],))
        else:
            c.execute('INSERT INTO accounts(id,username,salt,password_hash,created,is_operator) VALUES (?,?,?,?,?,1)',
                      (str(uuid.uuid4()),username,salt,pw_hash,time.time()))

def revoke_operator(username):
    """운영자 플래그만 해제. 계정·VC·서비스는 유지. PORTAL_ADMIN_USERS에 남아 있으면 계속 운영자."""
    with db() as c:
        cur=c.execute('UPDATE accounts SET is_operator=0 WHERE username=?',(username,))
        if cur.rowcount:
            c.execute('DELETE FROM account_sessions WHERE account_id=(SELECT id FROM accounts WHERE username=?)',(username,))
    return bool(cur.rowcount)


if __name__ == '__main__':
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--name', default='BLUEMAP Demo')
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    app.state.port, app.state.name = args.port, args.name
    ORIGINS.update({f'http://{h}:{args.port}' for h in ALLOWED_HOSTS})
    app.state.db = ROOT / 'data' / f'portal-{args.port}.sqlite3'
    # URLs contain capability keys; application activity log replaces raw access logs.
    uvicorn.run(app, host=args.host, port=args.port, access_log=False)
