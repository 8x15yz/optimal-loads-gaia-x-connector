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
            self.assertEqual(self.client.post('/accounts/register',json={'username':name,'password':'test-password-123'}).status_code,200)
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
        with patch.dict(os.environ,{'PORTAL_ALLOWED_DATA_ORIGINS':'https://weather.example'}), patch.object(p.httpx,'Client',side_effect=fake_client):
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

if __name__=='__main__':unittest.main(verbosity=2)
