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
        for name in ('alice','bobby'):
            self.assertEqual(self.client.post('/accounts/register',json={'username':name,'password':'test-password-123'}).status_code,200)
            self.users.append(self.login(name))
        now=datetime.now(timezone.utc)
        self.report={'profile':p.PROFILE,'eligible_for_demo':True,'summary':{'subject_id':'same-company','country':'KR','legal_name':'Test Company'},
            'verified_at':now.isoformat(),'valid_until':(now+timedelta(days=2)).isoformat(),'has_credential_status':False,
            'checks':[{'scope':'Test VC','name':'서명','status':'pass','detail':'TEST FIXTURE ONLY','required_for_demo':True}],
            'documents':[{'payload':{'validFrom':(now-timedelta(days=1)).isoformat(),'validUntil':(now+timedelta(days=2)).isoformat()}}]}
        self.stub=patch.object(p,'inspect',side_effect=lambda tokens:copy.deepcopy(self.report));self.stub.start()
        with p.db() as c:
            for i,user in enumerate(self.users):
                account=self.client.get('/accounts/me',headers=user).json()['account_id']
                c.execute('INSERT INTO imports VALUES (?,?,?,?,?)',(f'vc{i}','[]',json.dumps(self.report),account,p.time.time()))
        res=self.client.post('/service-offerings',headers=self.admin,json={'name':'Weather'})
        self.service=res.json()['service_offering_id']
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

if __name__=='__main__':unittest.main(verbosity=2)
