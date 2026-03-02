"""
Contract Review Tool - AI-Powered Contract Analysis
Copyright (c) 2024. All rights reserved.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
import anthropic
from werkzeug.utils import secure_filename
import io

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
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
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
            model="claude-sonnet-4-20250514",
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
    """Main page"""
    return render_template('index.html')

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

@app.route('/results')
def results():
    """Results page"""
    return render_template('results.html')

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
    
    app.run(debug=True, host='0.0.0.0', port=5000)