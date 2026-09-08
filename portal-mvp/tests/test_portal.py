"""Offline synthetic signatures only; these fixtures are NOT official Gaia-X credentials."""
import base64
import copy
import hashlib
import io
import json
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jwt
import pytest
import rfc8785
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
import credentials as vc
from portal import app

@pytest.fixture
def bundle():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    issuers = list(vc.TRUSTED)
    now = datetime.now(timezone.utc)
    def p(t, ident, subject, issuer):
        return {'@context':['https://www.w3.org/ns/credentials/v2'], 'type':['VerifiableCredential',t],
                'id':ident, 'issuer':issuer,'validFrom':(now-timedelta(minutes=1)).isoformat(),
                'validUntil':(now+timedelta(hours=1)).isoformat(),'credentialSubject':subject}
    docs = [p('gx:LegalPerson','urn:lp',{'id':'urn:company','schema:name':'Demo','gx:legalAddress':{'gx:countryCode':'KR'},'gx:registrationNumber':{'id':'urn:lei:subject'}},issuers[0]),
            p('gx:Issuer','urn:terms',{'id':'urn:terms:subject','gaiaxTermsAndConditions':'demo'},issuers[0]),
            p('gx:LeiCode','urn:lei',{'id':'urn:lei:subject','schema:leiCode':'DEMO'},issuers[1])]
    refs = [{'id':d['id'],'type':d['type'][1],'gx:digestSRI':'sha256-'+hashlib.sha256(rfc8785.dumps(d)).hexdigest()} for d in docs]
    docs.append(p('gx:LabelCredential','urn:compliance',{'id':'urn:compliance:subject','gx:compliantCredentials':refs,'gx:labelLevel':'SC','gx:rulesVersion':'CD25.10'},issuers[2]))
    def sign(d):
        return jwt.encode(d,key,algorithm='RS256' if d['issuer']==issuers[0] else 'PS256',headers={'kid':d['issuer']+'#key','typ':'vc+jwt','cty':'vc'})
    tokens = [(str(i)+'.jwt',sign(d)) for i,d in enumerate(docs)]
    vp = {'@context':['https://www.w3.org/ns/credentials/v2'],'type':'VerifiablePresentation','issuer':issuers[0],
          'validFrom':docs[0]['validFrom'],'validUntil':docs[0]['validUntil'],
          'verifiableCredential':[{'type':'EnvelopedVerifiableCredential','id':'data:application/vc+jwt,'+t} for _,t in tokens[:3]]}
    vp_token=jwt.encode(vp,key,algorithm='RS256',headers={'kid':issuers[0]+'#key','typ':'vp+jwt','cty':'vp'})
    def resolver(did):
        return {'id':did,'verificationMethod':[{'id':did+'#key','controller':did,'publicKeyJwk':public}],'assertionMethod':[did+'#key']}
    return {'tokens':tokens,'docs':docs,'sign':sign,'resolver':resolver,'vp':vp_token}

def test_vp_plus_compliance_and_dedup(bundle):
    b=bundle
    r=vc.inspect_set([('vp.jwt',b['vp']),b['tokens'][3]]+b['tokens'],b['resolver'])
    assert len(r['documents'])==5
    assert r['eligible_for_demo']
    assert all(c['status']=='pass' for c in r['checks'] if c['name']=='서명')
    assert not r['production_compliance']
    assert any(c['status']=='unknown' for c in r['checks'])

def test_bad_signature(bundle):
    tokens=bundle['tokens'].copy();h,p,s=tokens[0][1].split('.')
    sig=bytearray(base64.urlsafe_b64decode(s+'='*(-len(s)%4)));sig[0]^=1
    tokens[0]=('bad.jwt',h+'.'+p+'.'+base64.urlsafe_b64encode(sig).decode().rstrip('='))
    r=vc.inspect_set(tokens,bundle['resolver'])
    assert not r['eligible_for_demo']
    assert any(c['name']=='서명' and c['status']=='fail' for c in r['checks'])

def test_wrong_compliance_hash(bundle):
    d=copy.deepcopy(bundle['docs'][3]);d['credentialSubject']['gx:compliantCredentials'][0]['gx:digestSRI']='sha256-'+'0'*64
    r=vc.inspect_set(bundle['tokens'][:3]+[('bad-hash.jwt',bundle['sign'](d))],bundle['resolver'])
    assert not r['eligible_for_demo']
    assert any(c['name']=='Compliance ID·해시' and c['status']=='fail' for c in r['checks'])

def test_expired(bundle):
    d=copy.deepcopy(bundle['docs'][3]);d['validUntil']='2000-01-01T00:00:00Z'
    r=vc.inspect_set(bundle['tokens'][:3]+[('expired.jwt',bundle['sign'](d))],bundle['resolver'])
    assert not r['eligible_for_demo']
    assert any(c['name']=='유효기간' and c['status']=='fail' for c in r['checks'])

def test_unreachable_key(bundle):
    def offline(did): raise TimeoutError('offline')
    r=vc.inspect_set(bundle['tokens'],offline)
    assert not r['eligible_for_demo']
    assert all(c['status']=='unknown' for c in r['checks'] if c['name']=='서명')

def test_conflicting_id(bundle):
    d=copy.deepcopy(bundle['docs'][0]);d['credentialSubject']['schema:name']='changed'
    with pytest.raises(ValueError,match='동일 ID'):
        vc.inspect_set(bundle['tokens']+[('duplicate.jwt',bundle['sign'](d))],bundle['resolver'])

def test_unknown_issuer_not_fetched(bundle):
    d=copy.deepcopy(bundle['docs'][0]);d['issuer']='did:web:evil.example'
    def resolver(did):
        assert did!='did:web:evil.example';return bundle['resolver'](did)
    r=vc.inspect_set([('unknown.jwt',bundle['sign'](d))]+bundle['tokens'][1:],resolver)
    assert not r['eligible_for_demo']

def test_incomplete(bundle):
    assert not vc.inspect_set(bundle['tokens'][:3],bundle['resolver'])['eligible_for_demo']

def test_archive_validation():
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,'w') as z:z.writestr('nested.py','print(123)')
    with pytest.raises(ValueError):vc.read_uploads([('bad.zip',mem.getvalue())])

def test_invalid_compact():
    with pytest.raises(ValueError):vc.unpack('not-a-jwt')

@pytest.fixture
def client(tmp_path,bundle):
    app.state.db=tmp_path/'test.sqlite3';app.state.resolver=bundle['resolver']
    with TestClient(app) as c:yield c
    app.state.resolver=None

LOCAL={'X-Portal-Local':'1'}
_seq=[0]
def register_login(c):
    """Fresh account per call so parallel activate() calls don't collide on username."""
    _seq[0]+=1
    username='demo-user-'+str(_seq[0])
    r=c.post('/accounts/register',json={'username':username,'password':'demo-password-1'})
    assert r.status_code==200,r.text
    r=c.post('/accounts/login',json={'username':username,'password':'demo-password-1'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

def activate(c,b,account_auth=None):
    account_auth=account_auth or register_login(c)
    headers={**LOCAL,**account_auth}
    r=c.post('/credentials/import',headers=headers,files=[('files',(n,t.encode(),'application/octet-stream')) for n,t in b['tokens']])
    assert r.status_code==200,r.text
    ident=r.json()['id']
    session=c.post('/demo-sessions',headers=headers,json={'import_id':ident})
    assert session.status_code==200,session.text
    return {'Authorization':'Bearer '+session.json()['access_token']}

def test_import_policy_transfer(client,bundle):
    c=client;auth=activate(c,bundle)
    service=c.post('/service-offerings',headers=LOCAL,json={'name':'Weather','country':'KR'}).json()['service_offering_id']
    assert c.get('/catalog',headers=auth).json()['service_offerings'][0]['id']==service
    grant=c.post('/negotiate',headers=auth,json={'service_offering_id':service})
    assert grant.status_code==200
    cid=grant.json()['contract_id']
    assert c.post('/transfer',json={'contract_id':cid}).status_code==401
    assert c.post('/transfer',headers={'Authorization':'Bearer forged'},json={'contract_id':cid}).status_code==401
    result=c.post('/transfer',headers=auth,json={'contract_id':cid})
    assert result.status_code==200 and result.json()['data']['sample']
    other=c.post('/service-offerings',headers=LOCAL,json={'name':'Restricted','country':'DE'}).json()['service_offering_id']
    assert c.post('/negotiate',headers=auth,json={'service_offering_id':other}).status_code==403


def test_revalidation_blocks_transfer(client,bundle):
    auth=activate(client,bundle)
    sid=client.post('/service-offerings',headers=LOCAL,json={'name':'Weather'}).json()['service_offering_id']
    cid=client.post('/negotiate',headers=auth,json={'service_offering_id':sid}).json()['contract_id']
    def offline(did):raise TimeoutError()
    app.state.resolver=offline
    assert client.post('/transfer',headers=auth,json={'contract_id':cid}).status_code==403


def test_other_identity_cannot_use_grant(client,bundle):
    auth=activate(client,bundle)
    sid=client.post('/service-offerings',headers=LOCAL,json={'name':'Weather'}).json()['service_offering_id']
    cid=client.post('/negotiate',headers=auth,json={'service_offering_id':sid}).json()['contract_id']
    from portal import db
    # Simulate a second already authenticated demo identity.
    auth2=activate(client,bundle);token=auth2['Authorization'][7:]
    with db() as c:c.execute('UPDATE sessions SET participant_id=? WHERE token_hash=?',('demo:someone-else',hashlib.sha256(token.encode()).hexdigest()))
    assert client.post('/transfer',headers=auth2,json={'contract_id':cid}).status_code==403


def test_local_management_and_url_guards(client):
    assert client.post('/service-offerings',json={'name':'Bad'}).status_code==403
    assert client.post('/service-offerings',headers={**LOCAL,'Origin':'https://untrusted.example'},json={'name':'Bad'}).status_code==403
    assert client.post('/service-offerings',headers=LOCAL,json={'name':'Bad','data_url':'http://169.254.169.254/latest/'}).status_code==400
    assert client.get('/health').status_code==200
    assert client.get('/').status_code==200


def test_account_register_and_login(client):
    c=client
    assert c.post('/accounts/register',json={'username':'alice','password':'alice-secret-1'}).status_code==200
    assert c.post('/accounts/register',json={'username':'alice','password':'another-pass-1'}).status_code==409
    assert c.post('/accounts/register',json={'username':'a','password':'alice-secret-1'}).status_code==422  # pydantic min_length
    assert c.post('/accounts/register',json={'username':'alice2','password':'short'}).status_code==422  # pydantic min_length
    assert c.post('/accounts/register',json={'username':'has space','password':'alice-secret-1'}).status_code==400  # custom regex check
    assert c.post('/accounts/login',json={'username':'alice','password':'wrong-password'}).status_code==401
    assert c.post('/accounts/login',json={'username':'nobody','password':'whatever-1'}).status_code==401
    ok=c.post('/accounts/login',json={'username':'alice','password':'alice-secret-1'})
    assert ok.status_code==200 and ok.json()['username']=='alice'
    assert c.get('/accounts/me').status_code==401
    me=c.get('/accounts/me',headers={'Authorization':'Bearer '+ok.json()['access_token']})
    assert me.status_code==200 and me.json()['username']=='alice'


def test_credentials_require_login_and_are_scoped_to_account(client,bundle):
    c=client
    files=[('files',(n,t.encode(),'application/octet-stream')) for n,t in bundle['tokens']]
    # No login at all.
    assert c.post('/credentials/import',headers=LOCAL,files=files).status_code==401
    alice=register_login(c)
    imported=c.post('/credentials/import',headers={**LOCAL,**alice},files=files)
    assert imported.status_code==200,imported.text
    ident=imported.json()['id']
    mine=c.get('/accounts/me/credentials',headers=alice)
    assert mine.status_code==200
    assert len(mine.json()['credentials'])==1
    assert mine.json()['credentials'][0]['id']==ident
    # A second account can't see, recheck, or activate the first account's import.
    bob=register_login(c)
    assert c.get('/accounts/me/credentials',headers=bob).json()['credentials']==[]
    assert c.post('/credentials/recheck',headers={**LOCAL,**bob},json={'import_id':ident}).status_code==403
    assert c.post('/demo-sessions',headers={**LOCAL,**bob},json={'import_id':ident}).status_code==403
    # The owner can still recheck and activate it.
    assert c.post('/credentials/recheck',headers={**LOCAL,**alice},json={'import_id':ident}).status_code==200
    assert c.post('/demo-sessions',headers={**LOCAL,**alice},json={'import_id':ident}).status_code==200
    # A second import under the same account is added, not overwritten.
    imported2=c.post('/credentials/import',headers={**LOCAL,**alice},files=files)
    assert imported2.status_code==200
    assert len(c.get('/accounts/me/credentials',headers=alice).json()['credentials'])==2


def test_logout_invalidates_account_session(client):
    c=client
    alice=register_login(c)
    assert c.get('/accounts/me/credentials',headers=alice).status_code==200
    assert c.post('/accounts/logout',headers=alice).status_code==200
    assert c.get('/accounts/me/credentials',headers=alice).status_code==401
