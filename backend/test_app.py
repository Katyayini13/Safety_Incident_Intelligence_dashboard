from fastapi.testclient import TestClient
from backend.app import app, configured_cors_origins
from backend import services
c=TestClient(app)
def test_health():assert c.get('/health').json()['status']=='ok'
def test_demo_contract():
 r=c.get('/api/demo').json()
 assert r['status']=='ready' and r['records']==6
def test_cors_origin_list_is_environment_configurable(monkeypatch):
 monkeypatch.setenv('CORS_ORIGINS','https://ui.example.test/, https://admin.example.test')
 assert configured_cors_origins()==['https://ui.example.test','https://admin.example.test']
def test_cors_wildcard_is_rejected(monkeypatch):
 import pytest
 monkeypatch.setenv('CORS_ORIGINS','*')
 with pytest.raises(ValueError,match='wildcard origins are not allowed'):
  configured_cors_origins()
def test_local_frontend_preflight():
 r=c.options('/api/analyze',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'})
 assert r.status_code==200
 assert r.headers['access-control-allow-origin']=='http://localhost:5173'
def test_incidents():assert len(c.get('/api/incidents').json())==6
def test_incident_filter_contract():
 rows=c.get('/api/incidents',params={'category':'environment','severity':'high','q':'gearbox'}).json()
 assert rows and all(row['target_category']=='environment' and row['target_severity']=='high' for row in rows)
def test_analytics():assert c.get('/api/analytics').json()['analytics']['total']==6
def test_category():assert services.predict('Oil spill near gearbox')['category']=='environment'
def test_severity():assert services.predict('Electrical fire hazard')['severity']=='high'
def test_retrieval():assert services.retrieve('oil seepage gearbox')[0]['incident_id']=='S002'
def test_empty():
 try:services.predict('')
 except ValueError:return
 assert False
def test_empty_api():assert c.post('/api/analyze',json={'text':''}).status_code==422
def test_local():assert c.post('/api/analyze',json={'text':'Water leak at module cleaning'}).json()['explanation_source']=='local'
def test_upload_invalid():assert c.post('/api/incidents/upload',files={'file':('x.csv','foo\na\n','text/csv')}).status_code==422


def test_unseen_fluid_leak_is_environment_not_negated_injury():
 p=services.predict('A technician found a fractured hydraulic hose leaking fluid beside an inverter station; absorbent pads contained the leak, with no injury reported.')
 assert p['category']=='environment'
 assert p['severity']=='medium'
 assert 'injury' not in p['risk_indicators']

def test_unseen_incident_gets_environmental_control():
 r=services.analyze('Hydraulic fluid leaking from a hose; contained with absorbent pads and no injury.')
 assert r['explanation_source']=='local'
 assert any('containment' in x for x in r['recommendations'])

def test_upload_valid_csv():
 r=c.post('/api/incidents/upload',files={'file':('new.csv','narrative\nOil leak beside turbine\n','text/csv')})
 assert r.status_code==200 and r.json()['usable_narratives']==1

def test_negated_injury_is_not_a_positive_indicator():
 p=services.predict('A small hydraulic leak was contained; no injury reported.')
 assert p['severity']=='medium'
 assert 'injury' not in p['risk_indicators']
 assert not any('injury' in item for item in p['severity_indicators'])

def test_negated_fire_and_injury_do_not_trigger_high_severity():
 p=services.predict('Inspection confirmed no fire and no injury; a routine observation was logged.')
 assert p['severity']=='low'
 assert not any('fire' in item or 'injury' in item for item in p['severity_indicators'])

def test_electrical_hazard_has_explained_high_trigger():
 p=services.predict('An exposed live wire caused an electrical shock near the switch room.')
 assert p['severity']=='high'
 assert any('electrical shock or exposed energized equipment' in item for item in p['severity_indicators'])

def test_electrical_hazard_phrase_is_high():
 p=services.predict('An electrical hazard was found at the high-voltage cabinet.')
 assert p['severity']=='high'
 assert any('electrical hazard:' in item for item in p['severity_indicators'])

def test_ambiguous_multidomain_incident_is_deterministic_and_uncalibrated():
 text='A worker found oil leaking beside an electrical cabinet, with no injury reported.'
 first=services.predict(text); second=services.predict(text)
 assert first==second
 assert first['prediction_confidence'] is None
 assert first['severity']=='medium'
 assert 'injury' not in first['risk_indicators']

def test_unrelated_retrieval_is_suppressed_and_results_are_capped():
 assert services.retrieve('quarterly finance budget revenue margin')==[]
 assert len(services.retrieve('oil spill gearbox water leak vehicle near miss', k=99))<=3

def test_analysis_keeps_api_fields_and_adds_rule_explanation():
 result=services.analyze('A technician found a chemical spill beside the drainage channel.')
 assert {'input','summary','prediction','similar_incidents','recommendations','explanation_source','explanation','limitations'} <= result.keys()
 assert 'severity_indicators' in result['prediction']

def test_synthetic_evaluation_is_disclosed_and_separate():
 result=c.get('/api/analytics').json()['evaluation']
 assert {'target_category','target_severity'} <= result.keys()
 assert result['original_data']['records']==6
 assert result['synthetic_development']['records']==180
 assert 'synthetic' in result['synthetic_development']['data_disclosure'].lower()
 assert result['synthetic_development']['split']['group_isolation'] is True
 assert result['synthetic_development']['split']['inner_cv_group_isolation'] is True
 assert result['synthetic_development']['category_class_counts']=={'environment':60,'esg_compliance':60,'safety':60}
 assert result['synthetic_development']['severity_class_counts']=={'high':60,'low':60,'medium':60}
