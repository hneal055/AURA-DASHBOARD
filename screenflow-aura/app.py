"""
ScreenFlow AURA — AI-Powered Screenplay Analysis API
Rewritten from http.server to Flask with real Claude AI, SQLite persistence, and API key auth.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json
import hmac
import hashlib
import time
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
import anthropic

load_dotenv(override=True)

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────────

_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY is not set. Add it to your .env file.')
app.secret_key = _secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aura.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ── Model ───────────────────────────────────────────────────────────────────

class AuraAnalysis(db.Model):
    __tablename__ = 'aura_analyses'

    id = db.Column(db.Integer, primary_key=True)
    analysis_type = db.Column(db.String(32), default='parse')  # parse | analyze | validate | batch
    screenplay_excerpt = db.Column(db.Text)          # first 500 chars for reference
    word_count = db.Column(db.Integer, default=0)
    result_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    batch_size = db.Column(db.Integer, default=1)    # >1 for batch requests

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'word_count': self.word_count,
            'batch_size': self.batch_size,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'excerpt': (self.screenplay_excerpt or '')[:120] + '…'
            if len(self.screenplay_excerpt or '') > 120 else (self.screenplay_excerpt or ''),
        }


with app.app_context():
    db.create_all()


# ── Auth ─────────────────────────────────────────────────────────────────────

def _get_request_api_key():
    return (
        request.headers.get('X-API-Key') or
        request.args.get('api_key') or
        (request.get_json(silent=True) or {}).get('api_key')
    )


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        provided = _get_request_api_key()
        expected = os.environ.get('AURA_API_KEY', '')
        if not provided:
            return jsonify({'error': 'API key required', 'hint': 'Pass X-API-Key header'}), 401
        if not expected:
            return jsonify({'error': 'AURA_API_KEY not configured on server'}), 500
        if not hmac.compare_digest(
            hashlib.sha256(provided.encode()).digest(),
            hashlib.sha256(expected.encode()).digest()
        ):
            return jsonify({'error': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated


# ── Claude helper ─────────────────────────────────────────────────────────────

def _get_claude_client():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise RuntimeError('ANTHROPIC_API_KEY not configured')
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(prompt: str, max_tokens: int = 1500) -> dict:
    """Call Claude and parse JSON response. Raises on error."""
    client = _get_claude_client()
    message = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=max_tokens,
        messages=[{'role': 'user', 'content': prompt}]
    )
    text = message.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        text = text.rsplit('```', 1)[0]
    return json.loads(text)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    total = AuraAnalysis.query.count()
    return jsonify({
        'status': 'operational',
        'service': 'ScreenFlow AURA',
        'version': '3.0.0',
        'total_analyses': total,
        'timestamp': datetime.utcnow().isoformat(),
    })


@app.route('/api/parse', methods=['POST'])
@require_api_key
def parse():
    """Single screenplay parse — full AI analysis."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay content and return ONLY a valid JSON object — no markdown, no explanation, just JSON.

SCREENPLAY ({words} words):
{screenplay[:8000]}

Return this exact JSON structure:
{{
  "document_metrics": {{
    "word_count": {words},
    "estimated_pages": {round(words / 250, 1)},
    "primary_genre": "<genre>",
    "complexity_score": <integer 0-100>
  }},
  "quality_assessment": {{
    "overall_score": <integer 0-100>,
    "structure_quality": <integer 0-100>,
    "dialogue_effectiveness": <integer 0-100>,
    "pacing_analysis": "<excellent|good|balanced|slow|rushed>",
    "commercial_potential": "<HIGH|MEDIUM|LOW>"
  }},
  "ai_insights": {{
    "sentiment_analysis": {{
      "overall_sentiment": "<positive|neutral|complex|dark>",
      "emotional_arc": "<rising|falling|balanced|volatile>",
      "tone_consistency": "<consistent|varied|inconsistent>"
    }},
    "theme_detection": ["<theme1>", "<theme2>", "<theme3>"],
    "style_assessment": {{
      "writing_style": "<descriptive|dialogue_heavy|action_oriented|balanced>",
      "pacing": "<brisk|deliberate|varied|consistent>",
      "originality_score": <integer 0-100>
    }}
  }},
  "recommendations": ["<rec1>", "<rec2>", "<rec3>"]
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1200)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_metadata'] = {
            'processing_time_ms': elapsed_ms,
            'ai_model_used': 'claude-sonnet-4-6',
            'word_count_processed': words,
        }

        record = AuraAnalysis(
            analysis_type='parse',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'analysis': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze():
    """Deep narrative analysis — character arcs, commercial viability, market fit."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    analysis_type = data.get('analysis_type', 'comprehensive')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    prompt = f"""You are a professional Hollywood screenplay analyst doing a {analysis_type} analysis. Return ONLY a valid JSON object — no markdown, no explanation.

SCREENPLAY ({words} words):
{screenplay[:8000]}

Return this exact JSON structure:
{{
  "analysis_type": "{analysis_type}",
  "insights": {{
    "narrative_structure": {{
      "act_breakdown": {{"act1": "<assessment>", "act2": "<assessment>", "act3": "<assessment>"}},
      "plot_points": <integer>,
      "climax_strength": "<strong|moderate|weak>"
    }},
    "character_analysis": {{
      "main_characters": <integer>,
      "character_depth": "<shallow|moderate|deep|complex>",
      "character_arcs": <integer>,
      "protagonist_strength": "<compelling|adequate|weak>"
    }},
    "commercial_viability": {{
      "target_audience": "<broad|niche|premium|genre-specific>",
      "market_potential": "<HIGH|MEDIUM|LOW>",
      "comparable_titles": ["<title1>", "<title2>"],
      "distribution_outlook": "<theatrical|streaming|limited|festival>"
    }},
    "technical_assessment": {{
      "formatting_compliance": "<compliant|minor-issues|needs-revision>",
      "industry_standards": "<meets|partially-meets|below>",
      "readability_score": <integer 0-100>
    }}
  }},
  "recommendations": ["<rec1>", "<rec2>", "<rec3>"],
  "risk_assessment": {{
    "overall_risk": "<low|medium|high>",
    "commercial_risk": "<low|medium|high>",
    "technical_risk": "<low|medium|high>",
    "market_fit": "<strong|moderate|weak>"
  }}
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1500)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_time_ms'] = elapsed_ms
        result['ai_model'] = 'claude-sonnet-4-6'

        record = AuraAnalysis(
            analysis_type='analyze',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'analysis': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/validate', methods=['POST'])
@require_api_key
def validate():
    """Format and compliance validation."""
    data = request.get_json(silent=True) or {}
    screenplay = data.get('screenplay', '')
    if not screenplay.strip():
        return jsonify({'error': 'screenplay is required'}), 400

    start = time.time()
    words = len(screenplay.split())

    prompt = f"""You are a professional screenplay format validator. Validate the following screenplay against industry standards and return ONLY a valid JSON object.

SCREENPLAY ({words} words):
{screenplay[:6000]}

Return this exact JSON structure:
{{
  "compliance_report": {{
    "industry_standards": {{
      "hollywood_format": "<percent as string, e.g. 92%>",
      "final_draft_compatibility": "<percent>",
      "fountain_compatibility": "<percent>"
    }},
    "quality_metrics": {{
      "structure_integrity": "<percent>",
      "character_consistency": "<percent>",
      "dialogue_realism": "<percent>",
      "pacing_consistency": "<percent>"
    }}
  }},
  "issues": [
    {{"severity": "<critical|warning|suggestion>", "description": "<issue>", "location": "<where in script>"}}
  ],
  "overall_score": <integer 0-100>,
  "certification_status": "<compliant|conditionally-compliant|non-compliant>",
  "summary": "<2-sentence summary of validation result>"
}}"""

    try:
        result = _call_claude(prompt, max_tokens=1000)
        elapsed_ms = round((time.time() - start) * 1000)
        result['processing_time_ms'] = elapsed_ms

        record = AuraAnalysis(
            analysis_type='validate',
            screenplay_excerpt=screenplay[:500],
            word_count=words,
            result_json=json.dumps(result),
        )
        db.session.add(record)
        db.session.commit()
        result['analysis_id'] = record.id

        return jsonify({'success': True, 'validation': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/parse', methods=['POST'])
@require_api_key
def batch_parse():
    """Batch parse multiple screenplays — returns an array of analyses."""
    data = request.get_json(silent=True) or {}
    screenplays = data.get('screenplays', [])
    if not screenplays:
        return jsonify({'error': 'screenplays array is required'}), 400

    batch_start = time.time()
    results = []

    for i, item in enumerate(screenplays):
        text = item if isinstance(item, str) else item.get('content', '')
        label = f'item-{i+1}' if isinstance(item, str) else item.get('filename', f'item-{i+1}')
        words = len(text.split())

        prompt = f"""Analyze this screenplay excerpt and return ONLY a valid JSON object.

SCREENPLAY — {label} ({words} words):
{text[:4000]}

Return this exact JSON structure:
{{
  "item_id": "{label}",
  "document_metrics": {{
    "word_count": {words},
    "estimated_pages": {round(words / 250, 1)},
    "primary_genre": "<genre>"
  }},
  "quick_verdict": {{
    "overall_score": <integer 0-100>,
    "commercial_potential": "<HIGH|MEDIUM|LOW>",
    "recommendation": "<one-sentence recommendation>"
  }},
  "ai_analysis": {{
    "genre": "<genre>",
    "sentiment": "<positive|neutral|complex|dark>",
    "key_themes": ["<theme1>", "<theme2>"]
  }}
}}"""

        try:
            item_start = time.time()
            result = _call_claude(prompt, max_tokens=600)
            result['processing_time_ms'] = round((time.time() - item_start) * 1000)
            results.append(result)

            record = AuraAnalysis(
                analysis_type='batch',
                screenplay_excerpt=text[:500],
                word_count=words,
                result_json=json.dumps(result),
            )
            db.session.add(record)

        except Exception as e:
            results.append({
                'item_id': label,
                'error': str(e),
                'quick_verdict': {'overall_score': 0, 'commercial_potential': 'N/A', 'recommendation': 'Processing error'}
            })

    db.session.commit()
    total_ms = round((time.time() - batch_start) * 1000)

    # Store a summary batch record
    batch_record = AuraAnalysis(
        analysis_type='batch',
        screenplay_excerpt=f'Batch of {len(screenplays)} items',
        word_count=sum(len((s if isinstance(s, str) else s.get('content', '')).split()) for s in screenplays),
        result_json=json.dumps({'batch_results': results}),
        batch_size=len(screenplays),
    )
    db.session.add(batch_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'batch': {
            'batch_id': batch_record.id,
            'total_items': len(screenplays),
            'processed_items': sum(1 for r in results if 'error' not in r),
            'failed_items': sum(1 for r in results if 'error' in r),
            'total_processing_time_ms': total_ms,
        },
        'results': results,
    })


@app.route('/api/history')
@require_api_key
def history():
    """Return paginated list of past analyses from the database."""
    limit = min(int(request.args.get('limit', 50)), 200)
    offset = int(request.args.get('offset', 0))
    records = (
        AuraAnalysis.query
        .order_by(AuraAnalysis.created_at.desc())
        .offset(offset).limit(limit).all()
    )
    total = AuraAnalysis.query.count()
    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'records': [r.to_dict() for r in records],
    })


@app.route('/api/history/<int:record_id>')
@require_api_key
def history_detail(record_id):
    record = AuraAnalysis.query.get_or_404(record_id)
    data = record.to_dict()
    data['result'] = json.loads(record.result_json)
    return jsonify(data)


@app.route('/api/metrics')
@require_api_key
def metrics():
    """Real metrics from the database."""
    total = AuraAnalysis.query.count()
    by_type = db.session.query(
        AuraAnalysis.analysis_type,
        db.func.count(AuraAnalysis.id)
    ).group_by(AuraAnalysis.analysis_type).all()

    return jsonify({
        'total_analyses': total,
        'by_type': {t: c for t, c in by_type},
        'timestamp': datetime.utcnow().isoformat(),
    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('WARNING: ANTHROPIC_API_KEY not set — AI calls will fail')
    if not os.environ.get('AURA_API_KEY'):
        print('WARNING: AURA_API_KEY not set — all protected endpoints will return 500')
    app.run(debug=True, host='0.0.0.0', port=8083)
