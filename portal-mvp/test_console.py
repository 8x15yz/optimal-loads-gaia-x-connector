"""Offline integration tests. Successful VC reports are stubbed; cryptographic
verification is deliberately NOT claimed by these console lifecycle tests."""
import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import portal as p

def name_of(i): return ('alice','bobby','carol')[i]

class ConsoleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        p.app.state.db=Path(self.tmp.name)/'portal.sqlite3'
        self.env=patch.dict(os.environ,{'PORTAL_ADMIN_USERS':'rootuser'})
        self.env.start()
        p.bootstrap_admin('rootuser','test-password-123')
        self.client=TestClient(p.app)
        self.admin=self.login('rootuser')
        self.users=[]
        for name in ('alice','bobby','carol'):
            r=self.client.post('/accounts/register',json={'username':name,'password':'test-password-123'})
            self.assertEqual(r.status_code,200)
            self.assertEqual(self.client.post(f"/admin/accounts/{r.json()['account_id']}/approve",headers=self.admin).status_code,200)
            self.users.append(self.login(name))
        now=datetime.now(timezone.utc)
        self.report={'profile':p.PROFILE,'eligible_for_demo':True,'summary':{'subject_id':'same-company','country':'KR','legal_name':'Test Company'},
            'verified_at':now.isoformat(),'valid_until':(now+timedelta(days=2)).isoformat(),'has_credential_status':False,
            'checks':[{'scope':'Test VC','name':'서명','status':'pass','detail':'TEST FIXTURE ONLY','required_for_demo':True}],
            'documents':[{'payload':{'validFrom':(now-timedelta(days=1)).isoformat(),'validUntil':(now+timedelta(days=2)).isoformat()}}]}
        self.stub=patch.object(p,'inspect',side_effect=self.fake_inspect);self.stub.start()
        with p.db() as c:
            for i,user in enumerate(self.users):
                account=self.client.get('/accounts/me',headers=user).json()['account_id']
                # alice·bobby는 같은 회사 VC, carol은 다른 회사 VC
                subject='carol-company' if name_of(i)=='carol' else 'same-company'
                c.execute('INSERT INTO imports VALUES (?,?,?,?,?)',(f'vc{i}',json.dumps([subject]),json.dumps(self.report_for(subject)),account,p.time.time()))
        res=self.client.post('/service-offerings',headers=self.admin,json={'name':'Weather','platform_sample':True})
        self.service=res.json()['service_offering_id']
    def report_for(self,subject):
        r=copy.deepcopy(self.report);r['summary']['subject_id']=subject
        r['summary']['legal_name']='Carol Co' if subject=='carol-company' else 'Test Company';return r
    def fake_inspect(self,tokens):
        return self.report_for(tokens[0] if tokens else 'same-company')
    def tearDown(self):
        self.stub.stop(); self.env.stop();self.tmp.cleanup()
    def login(self,name):
        r=self.client.post('/accounts/login',json={'username':name,'password':'test-password-123'})
        return {'Authorization':'Bearer '+r.json()['access_token']}
    def act(self,action,user=0,**kw):
        return self.client.post('/console/'+action,headers=self.users[user],json=kw)
    def state(self,user=0): return self.client.get('/console/state',headers=self.users[user]).json()
    def connect(self,user=0):
        self.assertEqual(self.act('connect',user,import_id=f'vc{user}').status_code,200)
        return self.state(user)['access_path']+'/'+self.service
    def contract(self,user=0):self.assertEqual(self.act('contract',user,service_id=self.service).status_code,200)
    def test_complete_cycle_reset_and_stable_url(self):
        url=self.connect();self.assertEqual(self.client.get(url+'/ping').status_code,403)
        self.contract();self.assertEqual(self.client.get(url+'/ping').status_code,200)
        self.assertTrue(self.client.get(url+'/griddata').json()['sample'])
        self.act('reset');self.assertEqual(self.client.get(url+'/ping').status_code,403)
        self.assertEqual(url,self.connect());self.contract()
        self.assertEqual(self.client.get(url+'/ping').status_code,200)
    def test_same_vc_accounts_are_isolated(self):
        self.connect();self.contract();other=self.connect(1)
        self.assertEqual(self.client.get(other+'/griddata').status_code,403)
        target=self.state(1)['user']['id']
        self.assertEqual(self.act('reset',account_id=target).status_code,403)
        self.assertEqual(self.client.get('/console/logs?account_id='+target,headers=self.users[0]).status_code,403)
        self.assertEqual(self.act('delete-vc',import_id='vc1').status_code,403)
    def test_delete_vc_revokes_access_but_keeps_logs(self):
        url=self.connect();self.contract();self.act('delete-vc',import_id='vc0')
        self.assertEqual(self.client.get(url+'/griddata').status_code,403)
        state=self.state();self.assertFalse(state['sessions']);self.assertFalse(state['contracts'])
        logs=self.client.get('/console/logs',headers=self.users[0]).json()['logs']
        self.assertTrue(any(x['action']=='delete-vc' for x in logs))
        self.assertTrue(any(x['details'].get('checks') for x in logs))
        self.assertNotIn(url.split('/')[2],json.dumps(logs))
    def test_rotate_invalidates_previous_url(self):
        old=self.connect();self.contract();self.act('rotate-key')
        self.assertEqual(self.client.get(old+'/ping').status_code,403)
        new=self.state()['access_path']+'/'+self.service
        self.assertEqual(self.client.get(new+'/ping').status_code,200)
    def test_admin_and_country_policy(self):
        self.assertEqual(self.client.post('/service-offerings',headers=self.users[0],json={'name':'No'}).status_code,403)
        self.assertEqual(self.client.get('/admin/accounts',headers=self.users[0]).status_code,403)
        self.assertEqual(self.client.get('/admin/accounts',headers=self.admin).status_code,200)
        self.connect();target=self.state()['user']['id']
        self.assertEqual(self.client.post('/console/reset',headers=self.admin,json={'account_id':target}).status_code,200)
        self.connect();self.report['summary']['country']='US'
        self.assertEqual(self.act('contract',service_id=self.service).status_code,403)
    def test_failed_checks_block_connection_and_are_logged(self):
        self.report['eligible_for_demo']=False;self.report['checks'][0]['status']='fail'
        self.assertEqual(self.act('connect',import_id='vc0').status_code,403)
        log=self.client.get('/console/logs',headers=self.users[0]).json()['logs'][0]
        self.assertEqual(log['result'],'fail');self.assertEqual(log['details']['checks'][0]['status'],'fail')
    def test_expiration_revocation_and_path_allowlist(self):
        url=self.connect();self.contract()
        self.assertEqual(self.client.get(url+'/anything').status_code,404)
        self.act('revoke-contract',service_id=self.service)
        self.assertEqual(self.client.get(url+'/griddata').status_code,403)
        self.contract()
        with p.db() as c:c.execute('UPDATE sessions SET expires=0')
        self.assertEqual(self.client.get(url+'/ping').status_code,403)
    def test_real_parser_rejects_invalid_upload(self):
        self.stub.stop()
        r=self.client.post('/credentials/import',headers=self.users[0],files={'files':('bad.jwt',b'not a jwt')})
        self.assertEqual(r.status_code,400)
        logs=self.client.get('/console/logs',headers=self.users[0]).json()['logs']
        self.assertEqual(logs[0]['result'],'fail')
    def test_signup_requires_operator_approval(self):
        cred={'username':'dave','password':'test-password-123'}
        ident=self.client.post('/accounts/register',json=cred).json()['account_id']
        r=self.client.post('/accounts/login',json=cred)
        self.assertEqual(r.status_code,403);self.assertEqual(r.json()['detail'],'관리자 승인 대기 중입니다')
        r=self.client.post('/accounts/register',json=cred)
        self.assertEqual(r.status_code,409);self.assertEqual(r.json()['detail'],'가입 승인 대기 중인 아이디입니다')
        # 틀린 비밀번호로는 대기 상태를 알 수 없음
        self.assertEqual(self.client.post('/accounts/login',json={**cred,'password':'wrong-password-1'}).status_code,401)
        self.assertEqual(self.client.post(f'/admin/accounts/{ident}/approve',headers=self.users[0]).status_code,403)
        self.assertEqual(self.client.post(f'/admin/accounts/{ident}/approve',headers=self.admin).status_code,200)
        self.assertEqual(self.client.post('/accounts/login',json=cred).status_code,200)
        self.assertEqual(self.client.post('/accounts/register',json=cred).json()['detail'],'이미 사용 중인 아이디입니다')
    def test_reject_pending_signup_frees_username(self):
        cred={'username':'erin','password':'test-password-123'}
        ident=self.client.post('/accounts/register',json=cred).json()['account_id']
        self.assertEqual(self.client.post(f'/admin/accounts/{ident}/reject',headers=self.admin).status_code,200)
        self.assertEqual(self.client.post('/accounts/register',json=cred).status_code,200)
        approved=self.client.get('/accounts/me',headers=self.users[0]).json()['account_id']
        self.assertEqual(self.client.post(f'/admin/accounts/{approved}/reject',headers=self.admin).status_code,409)
    def test_admin_registration_reserved(self):
        r=self.client.post('/accounts/register',json={'username':'admin','password':'test-password-123'})
        self.assertEqual(r.status_code,403)
    def test_proxy_preserves_query_and_body_without_forwarding_auth(self):
        url=self.connect();self.contract()
        seen=[]
        def upstream(request):
            seen.append(request)
            return p.httpx.Response(200,content=b'{"grid":[1,2]}',headers={'content-type':'application/json'})
        original=p.httpx.Client
        def fake_client(**kwargs):
            return original(transport=p.httpx.MockTransport(upstream),**kwargs)
        with p.db() as c:c.execute('UPDATE services SET data_url=? WHERE id=?',('https://weather.example/api',self.service))
        with patch.dict(os.environ,{'PORTAL_ALLOWED_DATA_ORIGINS':'https://weather.example','PORTAL_ALLOWED_DATA_PATHS':'https://weather.example/api/griddata'}), patch.object(p.httpx,'Client',side_effect=fake_client):
            r=self.client.get(url+'/griddata?source=gfs&x=1&x=2',headers=self.users[0])
        self.assertEqual(r.status_code,200);self.assertEqual(r.json(),{'grid':[1,2]})
        self.assertEqual(str(seen[0].url),'https://weather.example/api/griddata?source=gfs&x=1&x=2')
        self.assertNotIn('authorization',seen[0].headers)

    def test_legacy_endpoints_account_ownership(self):
        # Original endpoints remain guarded with the same ownership rules.
        r=self.client.post('/demo-sessions',headers=self.users[0],json={'import_id':'vc0'});self.assertEqual(r.status_code,200)
        a={'Authorization':'Bearer '+r.json()['access_token']}
        r=self.client.post('/negotiate',headers=a,json={'service_offering_id':self.service});self.assertEqual(r.status_code,200)
        cid=r.json()['contract_id']
        r=self.client.post('/demo-sessions',headers=self.users[1],json={'import_id':'vc1'})
        b={'Authorization':'Bearer '+r.json()['access_token']}
        self.assertEqual(self.client.post('/transfer',headers=b,json={'contract_id':cid}).status_code,403)
        self.assertEqual(self.client.post('/transfer',headers=a,json={'contract_id':cid}).status_code,200)

    # ---- 0.5: 참여자 단일 역할 ----
    def provide(self,user=2,**kw):
        self.assertEqual(self.act('connect',user,import_id=f'vc{user}').status_code,200)
        r=self.client.post('/service-offerings',headers=self.users[user],json={'name':'Carol Grid',**kw})
        self.assertEqual(r.status_code,200,r.text);return r.json()
    def test_any_participant_can_provide_and_consume(self):
        sid=self.provide()['service_offering_id']
        self.connect(0)
        self.assertEqual(self.act('contract',0,service_id=sid).status_code,200)
        url=self.state(0)['access_path']+'/'+sid
        self.assertTrue(self.client.get(url+'/griddata').json()['sample'])
        carol=self.state(2)
        self.assertEqual(carol['provided_contracts'][0]['consumer_name'],'Test Company')
        self.assertTrue(next(s for s in carol['services'] if s['id']==sid)['mine'])
        # 같은 참여자가 소비자 역할도 수행: carol이 운영자 샘플 서비스를 계약
        self.assertEqual(self.act('contract',2,service_id=self.service).status_code,200)
        # 자기 서비스는 계약 불가
        self.assertEqual(self.act('contract',2,service_id=sid).status_code,403)
        # 원본 API 주소는 제공자 본인에게만
        self.assertNotIn('data_url',next(s for s in self.state(0)['services'] if s['id']==sid))
        self.assertIn('data_url',next(s for s in carol['services'] if s['id']==sid))
        self.assertFalse(self.state(0)['is_operator']);self.assertEqual(carol['participant']['legal_name'],'Carol Co')
    def test_same_participant_on_other_account_cannot_self_contract(self):
        sid=self.provide(0)['service_offering_id']
        self.connect(1)  # bobby: alice와 같은 회사 VC
        self.assertEqual(self.act('contract',1,service_id=sid).status_code,403)
    def test_provider_requirements_and_operator_sample_rules(self):
        r=self.client.post('/service-offerings',headers=self.users[2],json={'name':'NoSession'})
        self.assertEqual(r.status_code,403)
        r=self.client.post('/service-offerings',headers=self.admin,json={'name':'NoVC'})
        self.assertEqual(r.status_code,403)
        r=self.client.post('/service-offerings',headers=self.users[2],json={'name':'x','platform_sample':True})
        self.assertEqual(r.status_code,403)
        with patch.dict(os.environ,{'PORTAL_ALLOWED_DATA_ORIGINS':'https://weather.example'}):
            r=self.client.post('/service-offerings',headers=self.admin,json={'name':'x','platform_sample':True,'data_url':'https://weather.example/api'})
        self.assertEqual(r.status_code,400)
        self.act('connect',2,import_id='vc2')
        r=self.client.post('/service-offerings',headers=self.users[2],json={'name':'x','data_url':'https://not-allowed.example/api'})
        self.assertEqual(r.status_code,400)
        # 운영자는 대상 참여자 콘솔에서 대신 등록 가능(제공자는 대상 참여자)
        target=self.state(2)['user']['id']
        r=self.client.post('/service-offerings',headers=self.admin,json={'name':'OnBehalf','account_id':target})
        self.assertEqual(r.status_code,200)
        self.assertTrue(next(s for s in self.state(2)['services'] if s['name']=='OnBehalf')['mine'])
        other=self.state(0)['user']['id']
        self.assertEqual(self.client.post('/service-offerings',headers=self.users[2],json={'name':'x','account_id':other}).status_code,403)
    def test_provider_vc_deletion_suspends_service_but_reset_does_not(self):
        sid=self.provide()['service_offering_id']
        self.act('reset',2)
        self.connect(0);self.assertEqual(self.act('contract',0,service_id=sid).status_code,200)
        url=self.state(0)['access_path']+'/'+sid
        self.assertEqual(self.client.get(url+'/ping').status_code,200)
        self.act('delete-vc',2,import_id='vc2')
        self.assertEqual(self.client.get(url+'/griddata').status_code,403)
        self.assertFalse(next(s for s in self.state(0)['services'] if s['id']==sid)['active'])
        self.assertEqual(self.act('contract',0,service_id=sid).status_code,403)
    def test_service_delete_ownership(self):
        sid=self.provide()['service_offering_id']
        self.assertEqual(self.client.post(f'/service-offerings/{sid}/delete',headers=self.users[0]).status_code,403)
        self.assertEqual(self.client.post(f'/service-offerings/{self.service}/delete',headers=self.users[2]).status_code,403)
        self.assertEqual(self.client.post(f'/service-offerings/{sid}/delete',headers=self.users[2]).status_code,200)
        self.assertEqual(self.client.post(f'/admin/services/{self.service}/delete',headers=self.admin).status_code,200)
        self.assertFalse(self.state(0)['services'])
    def test_operator_flag_in_db_without_env_and_revoke(self):
        self.env.stop()
        try:
            p.bootstrap_admin('opsuser','test-password-123');ops=self.login('opsuser')
            self.assertEqual(self.client.get('/admin/accounts',headers=ops).status_code,200)
            self.assertTrue(self.client.get('/accounts/me',headers=ops).json()['is_operator'])
            self.assertEqual(self.client.get('/admin/accounts',headers=self.admin).status_code,200)
            self.assertTrue(p.revoke_operator('opsuser'))
            self.assertEqual(self.client.get('/admin/accounts',headers=ops).status_code,401)
            self.assertEqual(self.client.get('/admin/accounts',headers=self.login('opsuser')).status_code,403)
        finally:
            self.env.start()

    # ---- 데이터 API origin 허용 목록 ----
    def test_operator_manages_origin_allowlist_without_restart(self):
        A=self.admin
        self.assertEqual(self.client.post('/admin/data-origins',headers=self.users[2],json={'origin':'https://grid.example'}).status_code,403)
        self.assertEqual(self.client.get('/admin/data-origins',headers=self.users[2]).status_code,403)
        for bad in ('ftp://grid.example','https://grid.example/api','https://u:p@grid.example','http://127.0.0.1:9000',
                    'http://169.254.169.254','http://10.0.0.5','http://metadata.google.internal','http://localhost:8000','http://[::1]'):
            self.assertEqual(self.client.post('/admin/data-origins',headers=A,json={'origin':bad}).status_code,400,bad)
        r=self.client.post('/admin/data-origins',headers=A,json={'origin':'HTTPS://Grid.Example:443/','note':'carol'})
        self.assertEqual(r.status_code,200);self.assertEqual(r.json()['origin'],'https://grid.example')
        self.assertEqual(self.client.post('/admin/data-origins',headers=A,json={'origin':'https://grid.example'}).status_code,409)
        # 재시작 없이 참여자 등록 가능, 대소문자·기본포트 차이도 동일 origin으로 인정
        self.act('connect',2,import_id='vc2')
        r=self.client.post('/service-offerings',headers=self.users[2],json={'name':'Grid','data_url':'https://GRID.example:443/api'})
        self.assertEqual(r.status_code,200,r.text);sid=r.json()['service_offering_id']
        self.assertIn('https://grid.example',self.state(2)['data_origins'])
        listed=self.client.get('/admin/data-origins',headers=A).json()['origins']
        self.assertEqual(next(o for o in listed if o['origin']=='https://grid.example')['services'],1)
        self.connect(0);self.assertEqual(self.act('contract',0,service_id=sid).status_code,200)
        # 해제 즉시 제공 중지
        self.assertEqual(self.client.post('/admin/data-origins/delete',headers=A,json={'origin':'https://grid.example'}).status_code,200)
        url=self.state(0)['access_path']+'/'+sid
        self.assertEqual(self.client.get(url+'/ping').status_code,403)
        self.assertFalse(next(s for s in self.state(0)['services'] if s['id']==sid)['active'])
        self.assertEqual(self.client.post('/service-offerings',headers=self.users[2],json={'name':'x','data_url':'https://grid.example/api'}).status_code,400)
        logs=self.client.get('/console/logs?all_accounts=true',headers=A).json()['logs']
        self.assertTrue(any('origin 허용 해제' in l['summary'] for l in logs))
    def test_server_env_origins_are_listed_but_not_removable(self):
        with patch.dict(os.environ,{'PORTAL_ALLOWED_DATA_ORIGINS':'https://weather.example, bad-value'}):
            listed=self.client.get('/admin/data-origins',headers=self.admin).json()['origins']
            self.assertEqual([(o['origin'],o['source'],o['deletable']) for o in listed],[('https://weather.example','server',False)])
            self.assertEqual(self.client.post('/admin/data-origins/delete',headers=self.admin,json={'origin':'https://weather.example'}).status_code,400)
            self.assertEqual(self.client.post('/admin/data-origins',headers=self.admin,json={'origin':'https://weather.example'}).status_code,409)

    # ---- 데이터 API 경로 허용 목록 ----
    def external_service(self,base='https://grid.example/api'):
        """carol이 외부 API 서비스를 제공하고 alice가 계약한 상태를 만든다."""
        A=self.admin
        self.assertEqual(self.client.post('/admin/data-origins',headers=A,json={'origin':'https://grid.example'}).status_code,200)
        self.act('connect',2,import_id='vc2')
        r=self.client.post('/service-offerings',headers=self.users[2],json={'name':'Grid','data_url':base})
        self.assertEqual(r.status_code,200,r.text);sid=r.json()['service_offering_id']
        self.connect(0);self.assertEqual(self.act('contract',0,service_id=sid).status_code,200)
        return sid,self.state(0)['access_path']+'/'+sid
    def mock_upstream(self,handler):
        original=p.httpx.Client
        seen=[]
        def wrapped(request):
            seen.append(request);return handler(request)
        return patch.object(p.httpx,'Client',side_effect=lambda **kw: original(transport=p.httpx.MockTransport(wrapped),**kw)),seen
    def add_path(self,path,origin='https://grid.example',user=None):
        return self.client.post('/admin/data-paths',headers=user or self.admin,json={'origin':origin,'path':path})

    def test_normalize_path_rules(self):
        self.assertEqual(p.normalize_path('/api/s100/forecast-tiles/'),'/api/s100/forecast-tiles')
        for bad in ('api/griddata','/api//griddata','/api/../admin','/api/./x','/api/grid%2Ffile','/api/grid?x=1','/api/grid#x','/api/그리드','/'+'a'*400):
            with self.assertRaises(ValueError,msg=bad):p.normalize_path(bad)

    def test_operator_manages_paths_and_access_follows_immediately(self):
        sid,url=self.external_service()
        self.assertEqual(self.add_path('/api/gridfile',user=self.users[2]).status_code,403)
        self.assertEqual(self.add_path('/api/x',origin='https://not-allowed.example').status_code,400)
        self.assertEqual(self.add_path('/api/../x').status_code,400)
        for path in ('/api/griddata','/api/gridfile','/api/s100/forecast-tiles/'):
            self.assertEqual(self.add_path(path).status_code,200,path)
        self.assertEqual(self.add_path('/api/gridfile').status_code,409)
        listed=next(o for o in self.client.get('/admin/data-origins',headers=self.admin).json()['origins'] if o['origin']=='https://grid.example')
        self.assertEqual([x['path'] for x in listed['paths']],['/api/griddata','/api/gridfile','/api/s100/forecast-tiles'])
        self.assertEqual(listed['services'],1)
        # 이용자 카탈로그에는 base URL 하위 상대 경로만 노출, 원본 주소는 비노출
        svc=next(s for s in self.state(0)['services'] if s['id']==sid)
        self.assertEqual(svc['paths'],['griddata','gridfile','s100/forecast-tiles']);self.assertNotIn('data_url',svc)
        ctx,seen=self.mock_upstream(lambda req:p.httpx.Response(200,json={'ok':True}))
        with ctx:
            self.assertEqual(self.client.get(url+'/s100/forecast-tiles?product=s111&nw_lon=118.96').status_code,200)
            self.assertEqual(self.client.get(url+'/gridfile?source=noaa').status_code,200)
            self.assertEqual(self.client.get(url+'/latest').status_code,404)          # 미등록
            self.assertEqual(self.client.get(url+'/api/griddata').status_code,404)    # base 중복
            self.assertEqual(self.client.get(url+'/s100/%2E%2E/gridfile').status_code,404)  # 클라이언트 정규화를 피한 .. 세그먼트
            self.assertEqual(self.client.get(url+'/ping').status_code,200)            # ping은 목록과 무관
        self.assertEqual([str(r.url) for r in seen],['https://grid.example/api/s100/forecast-tiles?product=s111&nw_lon=118.96',
                                                     'https://grid.example/api/gridfile?source=noaa'])
        # 경로 해제는 해당 경로만 즉시 차단
        self.assertEqual(self.client.post('/admin/data-paths/delete',headers=self.admin,json={'origin':'https://grid.example','path':'/api/gridfile'}).status_code,200)
        with ctx:
            self.assertEqual(self.client.get(url+'/gridfile').status_code,404)
            self.assertEqual(self.client.get(url+'/griddata').status_code,200)
        # origin 해제 시 경로도 함께 정리
        self.client.post('/admin/data-origins/delete',headers=self.admin,json={'origin':'https://grid.example'})
        with p.db() as c:self.assertFalse(c.execute("SELECT 1 FROM data_origin_paths WHERE origin='https://grid.example'").fetchone())
        logs=self.client.get('/console/logs?all_accounts=true',headers=self.admin).json()['logs']
        self.assertTrue(any('경로 허용 해제' in l['summary'] for l in logs))
        denied=next(l for l in logs if l['details'].get('upstream_path')=='/api/latest')
        self.assertEqual(denied['result'],'fail')

    def test_unregistered_path_does_not_leak_before_contract(self):
        sid,url=self.external_service()
        self.act('revoke-contract',service_id=sid)
        self.assertEqual(self.client.get(url+'/gridfile').status_code,403)

    def test_upstream_errors_are_distinguished(self):
        sid,url=self.external_service();self.add_path('/api/griddata')
        cases=[(lambda r:p.httpx.Response(400,json={'detail':'lat is required'}),502,'HTTP 400'),
               (lambda r:p.httpx.Response(302,headers={'location':'https://evil.example'}),502,'리다이렉트'),
               (lambda r:p.httpx.Response(200,content=b'x'*(p.UPSTREAM_MAX_BYTES+1)),502,'크기 제한'),
               (lambda r:(_ for _ in ()).throw(p.httpx.ReadTimeout('slow')),504,'시간 초과'),
               (lambda r:(_ for _ in ()).throw(p.httpx.ConnectError('down')),502,'연결 실패')]
        for handler,status,text in cases:
            ctx,_=self.mock_upstream(handler)
            with ctx:r=self.client.get(url+'/griddata')
            self.assertEqual(r.status_code,status,text);self.assertIn(text,r.json()['detail'])
        self.assertTrue(any('lat is required' in l['summary'] for l in self.client.get('/console/logs',headers=self.users[0]).json()['logs']))

    def test_presigned_issuance_logs_object_keys_without_signature(self):
        sid,url=self.external_service();self.add_path('/api/s100/forecast-tiles');self.add_path('/api/latest')
        sig='https://bucket.s3.amazonaws.com/{k}?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=deadbeef'
        tiles={'expires_in_seconds':3600,'tiles':[{'s3_key':'s111/a_051.h5','presigned_url':sig.format(k='s111/a_051.h5')},
                                                  {'s3_key':'s111/a_052.h5','presigned_url':sig.format(k='s111/a_052.h5')}]}
        manifest={'issued':{'expires_in_seconds':900},'files':[{'url':sig.format(k='noaa/x.grib2')}]}
        for path,payload,keys,exp in (('s100/forecast-tiles',tiles,['s111/a_051.h5','s111/a_052.h5'],3600),('latest',manifest,['noaa/x.grib2'],900)):
            ctx,_=self.mock_upstream(lambda req,payload=payload:p.httpx.Response(200,json=payload))
            with ctx:self.assertEqual(self.client.get(url+'/'+path).status_code,200)
            log=self.client.get('/console/logs',headers=self.users[0]).json()['logs'][0]
            self.assertEqual(log['details']['issued_object_keys'],keys);self.assertEqual(log['details']['presigned_expires_in_seconds'],exp)
            self.assertEqual(log['details']['upstream_path'],'/api/'+path)
            self.assertNotIn('deadbeef',json.dumps(log))

    def test_server_env_paths_listed_effective_and_not_removable(self):
        env={'PORTAL_ALLOWED_DATA_ORIGINS':'https://grid.example','PORTAL_ALLOWED_DATA_PATHS':'https://grid.example/api/latest, https://grid.example/api/x?q=1, bad'}
        with patch.dict(os.environ,env):
            self.act('connect',2,import_id='vc2')
            sid=self.client.post('/service-offerings',headers=self.users[2],json={'name':'Grid','data_url':'https://grid.example/api/'}).json()['service_offering_id']
            listed=self.client.get('/admin/data-origins',headers=self.admin).json()['origins'][0]
            self.assertEqual([(x['path'],x['source'],x['deletable']) for x in listed['paths']],[('/api/latest','server',False)])
            self.assertEqual(self.add_path('/api/latest').status_code,409)
            self.assertEqual(self.client.post('/admin/data-paths/delete',headers=self.admin,json={'origin':'https://grid.example','path':'/api/latest'}).status_code,400)
            self.assertEqual(next(s for s in self.state(2)['services'] if s['id']==sid)['paths'],['latest'])

    def test_first_migration_seeds_legacy_paths_for_existing_services(self):
        import sqlite3
        path=Path(self.tmp.name)/'legacy.sqlite3'
        conn=sqlite3.connect(path)
        conn.executescript("""CREATE TABLE services(id TEXT PRIMARY KEY, name TEXT, data_url TEXT, country TEXT);
            CREATE TABLE data_origins(origin TEXT PRIMARY KEY, note TEXT, created REAL, created_by TEXT);""")
        conn.execute("INSERT INTO services VALUES ('s1','W','https://weather-api.bmap.kr/api/','KR')")
        conn.execute("INSERT INTO services VALUES ('s2','D','demo://weather','KR')")
        conn.execute("INSERT INTO data_origins VALUES ('https://weather-api.bmap.kr','',0,NULL)");conn.commit();conn.close()
        old=p.app.state.db;p.app.state.db=path
        try:
            self.assertEqual(p.allowed_data_paths('https://weather-api.bmap.kr'),{'/api/griddata','/api/latest'})
            with p.db() as c:c.execute("DELETE FROM data_origin_paths")
            self.assertEqual(p.allowed_data_paths('https://weather-api.bmap.kr'),set())  # 재실행 시 다시 채우지 않음
        finally:p.app.state.db=old

if __name__=='__main__':unittest.main(verbosity=2)
