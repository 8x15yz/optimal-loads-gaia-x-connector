"""Offline SHACL subset for this portal, not the complete official shape suite."""
import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from rdflib import Graph, URIRef, Namespace
from pyshacl import validate
from verification_support import result

ROOT = Path(__file__).resolve().parent / 'schemas'
URLS = {'https://www.w3.org/ns/credentials/v2':'w3c','https://www.w3.org/ns/credentials/examples/v2':'examples','https://w3id.org/gaia-x/development':'gaia','https://w3id.org/gaia-x/development#':'gaia'}
PREFIXES = {'schema':'https://schema.org/','vcard':'http://www.w3.org/2006/vcard/ns#'}
SH = Namespace('http://www.w3.org/ns/shacl#')
S = Namespace('urn:portal:shape:')

@lru_cache(maxsize=1)
def assets():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    for name,digest in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest: raise ValueError('고정 스키마 파일 해시 불일치: '+name)
    return {k:json.loads((ROOT/'contexts'/f'{k}.json').read_text())['@context'] for k in set(URLS.values())}

def inline_contexts(obj, contexts):
    def context(v):
        if isinstance(v,str):
            if v not in URLS: raise ValueError('이 프로필에서 고정하지 않은 JSON-LD context')
            return copy.deepcopy(contexts[URLS[v]])
        if isinstance(v,list): return [context(x) for x in v]
        if isinstance(v,dict) and all(k in PREFIXES and PREFIXES[k]==val for k,val in v.items()): return v
        raise ValueError('JSON-LD context 재정의 또는 미지원 context')
    if isinstance(obj,dict):
        return {k:context(v) if k=='@context' else inline_contexts(v,contexts) for k,v in obj.items()}
    if isinstance(obj,list): return [inline_contexts(v,contexts) for v in obj]
    return obj

def schema_check(payload,typ):
    try:
        data=inline_contexts(payload,assets())
        if typ=='VerifiablePresentation':
            return result('shacl','포털 SHACL','not_applicable','허용 context 확인; VP는 envelope 구조로 별도 검사',False)
        graph=Graph().parse(data=json.dumps(data),format='json-ld')
        shapes=Graph().parse(ROOT/'loire-demo-v2.ttl',format='turtle')
        shapes.add((S[typ.split(':')[-1]],SH.targetNode,URIRef(payload['id'])))
        conforms,report,_=validate(graph,shacl_graph=shapes,inference='none',advanced=False,js=False,do_owl_imports=False)
        messages=[str(m) for m in report.objects(None,SH.resultMessage)]
        return result('shacl','포털 SHACL','pass' if conforms else 'fail','고정 context와 포털 자체 SHACL 부분집합 통과 (공식 전체 아님)' if conforms else '; '.join(messages)[:500])
    except Exception as e:
        return result('shacl','포털 SHACL','fail','스키마 처리 실패: '+str(e)[:250])
