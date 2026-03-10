"""
ScreenFlow AURA — Test Suite
Run with: pytest tests/ -v
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

# Point to a throwaway in-memory DB during tests
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('AURA_API_KEY', 'test-api-key')
os.environ.setdefault('ANTHROPIC_API_KEY', 'test-anthropic-key')

from app import app, db

VALID_KEY = 'test-api-key'
HEADERS = {'X-API-Key': VALID_KEY}
SAMPLE_SCREENPLAY = (
    "INT. COFFEE SHOP - DAY\n\n"
    "ALICE (30s, intense) stares at her laptop screen.\n\n"
    "ALICE\nI can't believe they rejected the script.\n\n"
    "BOB\nKeep writing. That's all we can do.\n\n" * 20
)

MOCK_PARSE_RESPONSE = json.dumps({
    "document_metrics": {
        "word_count": 200, "estimated_pages": 0.8,
        "primary_genre": "drama", "complexity_score": 72
    },
    "quality_assessment": {
        "overall_score": 80, "structure_quality": 75,
        "dialogue_effectiveness": 85, "pacing_analysis": "good",
        "commercial_potential": "MEDIUM"
    },
    "ai_insights": {
        "sentiment_analysis": {"overall_sentiment": "complex", "emotional_arc": "rising", "tone_consistency": "consistent"},
        "theme_detection": ["perseverance", "rejection", "creativity"],
        "style_assessment": {"writing_style": "dialogue_heavy", "pacing": "brisk", "originality_score": 78}
    },
    "recommendations": ["Strengthen act 2", "Add more visual description", "Develop Bob's character arc"]
})

MOCK_ANALYZE_RESPONSE = json.dumps({
    "analysis_type": "comprehensive",
    "insights": {
        "narrative_structure": {"act_breakdown": {"act1": "solid", "act2": "needs work", "act3": "strong"}, "plot_points": 5, "climax_strength": "strong"},
        "character_analysis": {"main_characters": 2, "character_depth": "moderate", "character_arcs": 2, "protagonist_strength": "compelling"},
        "commercial_viability": {"target_audience": "broad", "market_potential": "MEDIUM", "comparable_titles": ["Whiplash", "The Wrestler"], "distribution_outlook": "streaming"},
        "technical_assessment": {"formatting_compliance": "compliant", "industry_standards": "meets", "readability_score": 82}
    },
    "recommendations": ["Consider a third act twist", "Tighten dialogue", "Expand the world-building"],
    "risk_assessment": {"overall_risk": "low", "commercial_risk": "medium", "technical_risk": "low", "market_fit": "strong"}
})

MOCK_VALIDATE_RESPONSE = json.dumps({
    "compliance_report": {
        "industry_standards": {"hollywood_format": "94%", "final_draft_compatibility": "90%", "fountain_compatibility": "96%"},
        "quality_metrics": {"structure_integrity": "88%", "character_consistency": "92%", "dialogue_realism": "85%", "pacing_consistency": "89%"}
    },
    "issues": [{"severity": "suggestion", "description": "Scene headings could be more specific", "location": "Act 1, Scene 3"}],
    "overall_score": 91,
    "certification_status": "compliant",
    "summary": "Script meets Hollywood formatting standards. Minor suggestions noted."
})


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # Force test API key — load_dotenv(override=True) runs at import time so we
    # must set this again here; the decorator reads os.environ at request time.
    orig_aura_key = os.environ.get('AURA_API_KEY')
    os.environ['AURA_API_KEY'] = VALID_KEY
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
    if orig_aura_key is None:
        os.environ.pop('AURA_API_KEY', None)
    else:
        os.environ['AURA_API_KEY'] = orig_aura_key


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_no_auth_required(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'operational'
    assert 'total_analyses' in data


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_parse_requires_auth(client):
    resp = client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY})
    assert resp.status_code == 401
    assert 'API key required' in resp.get_json()['error']


def test_parse_rejects_wrong_key(client):
    resp = client.post('/api/parse',
                       json={'screenplay': SAMPLE_SCREENPLAY},
                       headers={'X-API-Key': 'wrong-key'})
    assert resp.status_code == 403


def test_auth_via_query_param(client):
    """API key can also be passed as ?api_key= query param."""
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        resp = client.post(f'/api/parse?api_key={VALID_KEY}',
                           json={'screenplay': SAMPLE_SCREENPLAY})
    assert resp.status_code == 200


# ── Parse ─────────────────────────────────────────────────────────────────────

def test_parse_missing_screenplay(client):
    resp = client.post('/api/parse', json={}, headers=HEADERS)
    assert resp.status_code == 400


def test_parse_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        resp = client.post('/api/parse',
                           json={'screenplay': SAMPLE_SCREENPLAY},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'analysis' in data
    assert data['analysis']['quality_assessment']['overall_score'] == 80
    assert 'analysis_id' in data['analysis']


def test_parse_persists_to_db(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)
    resp = client.get('/api/metrics', headers=HEADERS)
    assert resp.get_json()['total_analyses'] >= 1


# ── Analyze ───────────────────────────────────────────────────────────────────

def test_analyze_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_ANALYZE_RESPONSE)):
        resp = client.post('/api/analyze',
                           json={'screenplay': SAMPLE_SCREENPLAY, 'analysis_type': 'comprehensive'},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['analysis']['insights']['character_analysis']['main_characters'] == 2


# ── Validate ──────────────────────────────────────────────────────────────────

def test_validate_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_VALIDATE_RESPONSE)):
        resp = client.post('/api/validate',
                           json={'screenplay': SAMPLE_SCREENPLAY},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['validation']['overall_score'] == 91
    assert data['validation']['certification_status'] == 'compliant'


# ── Batch ─────────────────────────────────────────────────────────────────────

MOCK_BATCH_ITEM = json.dumps({
    "item_id": "item-1",
    "document_metrics": {"word_count": 100, "estimated_pages": 0.4, "primary_genre": "drama"},
    "quick_verdict": {"overall_score": 78, "commercial_potential": "MEDIUM", "recommendation": "Promising concept."},
    "ai_analysis": {"genre": "drama", "sentiment": "complex", "key_themes": ["loss", "hope"]}
})


def test_batch_missing_screenplays(client):
    resp = client.post('/api/batch/parse', json={}, headers=HEADERS)
    assert resp.status_code == 400


def test_batch_success(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_BATCH_ITEM)):
        resp = client.post('/api/batch/parse',
                           json={'screenplays': [SAMPLE_SCREENPLAY, SAMPLE_SCREENPLAY]},
                           headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['batch']['total_items'] == 2
    assert len(data['results']) == 2


# ── History ───────────────────────────────────────────────────────────────────

def test_history_empty(client):
    resp = client.get('/api/history', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total'] == 0
    assert data['records'] == []


def test_history_after_analysis(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)

    resp = client.get('/api/history', headers=HEADERS)
    data = resp.get_json()
    assert data['total'] >= 1
    record = data['records'][0]
    assert record['analysis_type'] == 'parse'
    assert 'created_at' in record


def test_history_detail(client):
    with patch('app._call_claude', return_value=json.loads(MOCK_PARSE_RESPONSE)):
        parse_resp = client.post('/api/parse', json={'screenplay': SAMPLE_SCREENPLAY}, headers=HEADERS)
    record_id = parse_resp.get_json()['analysis']['analysis_id']

    resp = client.get(f'/api/history/{record_id}', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'result' in data


# ── Metrics ───────────────────────────────────────────────────────────────────

def test_metrics(client):
    resp = client.get('/api/metrics', headers=HEADERS)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_analyses' in data
    assert 'by_type' in data
