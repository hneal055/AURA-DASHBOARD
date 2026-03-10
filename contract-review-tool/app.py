"""
Contract Review Tool - AI-Powered Contract Analysis
Copyright (c) 2024. All rights reserved.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
import anthropic
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import io

load_dotenv(override=True)

# Import document processing libraries
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    if not PYPDF_AVAILABLE:
        return "PDF processing not available. Please install pypdf."
    
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        return "DOCX processing not available. Please install python-docx."
    
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"

def extract_text_from_file(file_path, filename):
    """Extract text from uploaded file based on extension"""
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading text file: {str(e)}"
    else:
        return "Unsupported file format"

def analyze_contract_with_ai(contract_text):
    """Send contract to Claude API for analysis"""
    
    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            'error': 'API key not configured. Please set ANTHROPIC_API_KEY environment variable.'
        }
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are an expert contract analyst. Analyze the following contract and provide a comprehensive review.

CONTRACT TEXT:
{contract_text}

Please provide a detailed analysis in the following structure:

1. KEY TERMS:
List and explain all important terms including:
- Parties involved
- Contract duration
- Payment terms
- Deliverables/obligations
- Termination conditions
- Renewal terms

2. RISK ANALYSIS:
Identify potential risks and problematic clauses:
- Rate each risk as HIGH, MEDIUM, or LOW
- Explain why each is a risk
- Quote the specific clause from the contract

3. FAIRNESS ASSESSMENT:
Overall assessment: FAVORABLE, NEUTRAL, or UNFAVORABLE
Explain your reasoning.

4. NEGOTIATION POINTS:
Provide 3-5 specific suggestions for negotiation:
- What to ask for
- Specific language to propose
- Why this matters

Be specific, quote relevant clauses, and provide actionable insights."""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse the response into structured data
        analysis = parse_ai_response(response_text)
        analysis['raw_response'] = response_text
        
        return analysis
        
    except Exception as e:
        return {
            'error': f'Error analyzing contract: {str(e)}'
        }

def parse_ai_response(response_text):
    """Parse Claude's response into structured data"""
    
    sections = {
        'key_terms': [],
        'risks': [],
        'fairness': 'NEUTRAL',
        'negotiation_points': []
    }
    
    # Simple parsing - split by sections
    lines = response_text.split('\n')
    current_section = None
    current_item = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        if 'KEY TERMS' in line.upper():
            current_section = 'key_terms'
        elif 'RISK ANALYSIS' in line.upper():
            current_section = 'risks'
        elif 'FAIRNESS' in line.upper():
            current_section = 'fairness'
        elif 'NEGOTIATION' in line.upper():
            current_section = 'negotiation_points'
        elif line.startswith('-') or line.startswith('•'):
            # This is a bullet point
            if current_item:
                # Save previous item
                if current_section == 'key_terms':
                    sections['key_terms'].append(' '.join(current_item))
                elif current_section == 'risks':
                    sections['risks'].append(' '.join(current_item))
                elif current_section == 'negotiation_points':
                    sections['negotiation_points'].append(' '.join(current_item))
            current_item = [line[1:].strip()]
        else:
            if current_item:
                current_item.append(line)
    
    # Don't forget the last item
    if current_item:
        if current_section == 'key_terms':
            sections['key_terms'].append(' '.join(current_item))
        elif current_section == 'risks':
            sections['risks'].append(' '.join(current_item))
        elif current_section == 'negotiation_points':
            sections['negotiation_points'].append(' '.join(current_item))
    
    # Extract fairness rating
    for line in lines:
        if 'FAVORABLE' in line.upper():
            sections['fairness'] = 'FAVORABLE'
            break
        elif 'UNFAVORABLE' in line.upper():
            sections['fairness'] = 'UNFAVORABLE'
            break
    
    return sections

@app.route('/')
def index():
    """Dashboard — redirect to analyze"""
    return render_template('analyze.html')

@app.route('/analyze')
def analyze():
    """Analyze page"""
    return render_template('analyze.html')

@app.route('/batch')
def batch():
    """Batch analysis page"""
    return render_template('batch.html')

@app.route('/contract')
def contract():
    """Contract review upload page"""
    return render_template('contract.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    
    if 'contract' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['contract']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF, DOCX, or TXT'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        contract_text = extract_text_from_file(file_path, filename)
        
        # Clean up file
        os.remove(file_path)
        
        if not contract_text or len(contract_text.strip()) < 100:
            return jsonify({'error': 'Could not extract enough text from the file. Please ensure it contains a readable contract.'}), 400
        
        # Analyze with AI
        analysis = analyze_contract_with_ai(contract_text)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 500
        
        # Add metadata
        analysis['filename'] = filename
        analysis['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """JSON endpoint for screenplay analysis"""
    import time
    data = request.get_json()
    if not data or not data.get('screenplay'):
        return jsonify({'success': False, 'error': 'No screenplay content provided'}), 400

    screenplay_text = data['screenplay']
    writer_info = data.get('writer_info', {})

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'success': False, 'error': 'ANTHROPIC_API_KEY not configured'}), 500

    try:
        client = anthropic.Anthropic(api_key=api_key)
        start_time = time.time()

        writer_context = ''
        if writer_info.get('name'):
            writer_context = f"\nWriter: {writer_info['name']} ({writer_info.get('experience', 'unknown experience')})"

        prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay content and return ONLY a valid JSON object — no markdown, no explanation, just the JSON.{writer_context}

SCREENPLAY:
{screenplay_text}

Return this exact JSON structure:
{{
  "quick_verdict": {{
    "commercial_score": <integer 0-100>,
    "recommendation": "<one-sentence recommendation>",
    "priority_level": "<HIGH PRIORITY | MEDIUM PRIORITY | LOW PRIORITY>",
    "estimated_roi": "<e.g. 2.5x-4x>"
  }},
  "detailed_analysis": {{
    "structural_breakdown": {{
      "pacing_score": <integer 0-100>,
      "act_breakdown": {{"act1": "<assessment>", "act2": "<assessment>", "act3": "<assessment>"}}
    }},
    "character_analysis": {{
      "main_characters": "<comma-separated list>",
      "character_depth_score": <integer 0-100>
    }},
    "market_potential": {{
      "market_potential": "<HIGH | MEDIUM | LOW> — <brief reason>",
      "target_audience": "<description>"
    }}
  }},
  "technical_metrics": {{
    "document_metrics": {{
      "primary_genre": "<genre>",
      "estimated_pages": <integer>,
      "character_count": <integer>
    }},
    "processing_time": "<X.Xs>"
  }}
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        elapsed = round(time.time() - start_time, 1)
        response_text = message.content[0].text.strip()

        # Strip markdown code fences if present
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            response_text = response_text.rsplit('```', 1)[0]

        result = json.loads(response_text)
        result['technical_metrics']['processing_time'] = f"{elapsed}s"

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/results')
def results():
    """Results page"""
    return render_template('results.html')

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded file without analyzing — used by frontend for PDF/DOCX"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        text = extract_text_from_file(file_path, filename)
        os.remove(file_path)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch/analyze', methods=['POST'])
def api_batch_analyze():
    """Batch screenplay analysis — processes multiple screenplays sequentially"""
    import time
    data = request.get_json()
    if not data or not data.get('screenplays'):
        return jsonify({'success': False, 'error': 'No screenplays provided'}), 400

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'success': False, 'error': 'ANTHROPIC_API_KEY not configured'}), 500

    client = anthropic.Anthropic(api_key=api_key)
    results = []

    for item in data['screenplays']:
        screenplay_text = item.get('content', '')
        writer_info = item.get('writer_info', {})
        filename = item.get('filename', 'Unknown')

        if not screenplay_text.strip():
            continue

        try:
            start_time = time.time()
            writer_context = ''
            if writer_info.get('name'):
                writer_context = f"\nWriter: {writer_info['name']} ({writer_info.get('experience', 'unknown')})"

            prompt = f"""You are a professional Hollywood screenplay analyst. Analyze the following screenplay and return ONLY a valid JSON object — no markdown, no explanation, just the JSON.{writer_context}

SCREENPLAY:
{screenplay_text}

Return this exact JSON structure:
{{
  "assessment_id": "{filename}",
  "quick_verdict": {{
    "commercial_score": <integer 0-100>,
    "recommendation": "<one-sentence recommendation>",
    "priority_level": "<HIGH PRIORITY | MEDIUM PRIORITY | LOW PRIORITY>",
    "estimated_roi": "<e.g. 2.5x-4x>"
  }},
  "technical_metrics": {{
    "document_metrics": {{
      "primary_genre": "<genre>",
      "estimated_pages": <integer>,
      "character_count": <integer>
    }},
    "processing_time": "<X.Xs>"
  }}
}}"""

            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )

            elapsed = round(time.time() - start_time, 1)
            response_text = message.content[0].text.strip()

            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('```', 1)[0]

            result = json.loads(response_text)
            result['technical_metrics']['processing_time'] = f"{elapsed}s"
            results.append(result)

        except Exception as e:
            results.append({
                'assessment_id': filename,
                'error': str(e),
                'quick_verdict': {'commercial_score': 0, 'recommendation': 'Error during processing', 'priority_level': 'LOW PRIORITY', 'estimated_roi': 'N/A'},
                'technical_metrics': {'document_metrics': {'primary_genre': 'Unknown', 'estimated_pages': 0, 'character_count': 0}, 'processing_time': '0s'}
            })

    return jsonify({'success': True, 'results': results})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'pypdf_available': PYPDF_AVAILABLE,
        'docx_available': DOCX_AVAILABLE
    })

if __name__ == '__main__':
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
