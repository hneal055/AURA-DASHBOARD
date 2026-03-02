"""
Scene Reader Studio Technologies - Web Interface
Professional Web Frontend for AURA Enterprise Platform
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
from aura_processor import ScreenFlowAURAProcessor
from screenflow_dashboard import ScreenFlowDashboard

app = Flask(__name__)
app.secret_key = 'scene-reader-tech-2024-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Scene Reader components
processor = ScreenFlowAURAProcessor()
dashboard = ScreenFlowDashboard()
dashboard.set_processor(processor)

class WebInterface:
    """Web interface for Scene Reader Studio Technologies"""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.fountain', '.pdf', '.docx']
        self.max_file_size = 16 * 1024 * 1024  # 16MB

@app.route('/')
def index():
    """Main dashboard page"""
    stats = dashboard.db.get_statistics()
    recent_assessments = dashboard.db.get_recent_assessments(5)
    
    return render_template('index.html', 
                         stats=stats,
                         recent_assessments=recent_assessments,
                         company="Scene Reader Studio Technologies")

@app.route('/analyze')
def analyze_page():
    """Single screenplay analysis page"""
    return render_template('analyze.html', 
                         company="Scene Reader Studio Technologies")

@app.route('/batch')
def batch_page():
    """Batch processing page"""
    return render_template('batch.html',
                         company="Scene Reader Studio Technologies")

@app.route('/api/analyze', methods=['POST'])
def analyze_screenplay():
    """API endpoint for screenplay analysis"""
    try:
        data = request.get_json()
        
        if not data or 'screenplay' not in data:
            return jsonify({'error': 'No screenplay content provided'}), 400
        
        screenplay_content = data['screenplay']
        writer_info = data.get('writer_info', {})
        
        if len(screenplay_content.strip()) < 50:
            return jsonify({'error': 'Screenplay content too short (minimum 50 characters)'}), 400
        
        # Perform Scene Reader analysis
        result = processor.analyze_screenplay(screenplay_content, writer_info)
        
        # Store in dashboard database
        dashboard.db.store_assessment(result)
        
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Analysis completed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/batch/analyze', methods=['POST'])
def batch_analyze():
    """API endpoint for batch screenplay analysis"""
    try:
        data = request.get_json()
        
        if not data or 'screenplays' not in data:
            return jsonify({'error': 'No screenplays provided'}), 400
        
        screenplays = data['screenplays']
        results = []
        
        for i, screenplay_data in enumerate(screenplays):
            screenplay_content = screenplay_data.get('content', '')
            writer_info = screenplay_data.get('writer_info', {})
            
            if len(screenplay_content.strip()) >= 50:
                result = processor.analyze_screenplay(screenplay_content, writer_info)
                dashboard.db.store_assessment(result)
                results.append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Batch analysis completed: {len(results)} screenplays processed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Batch analysis failed: {str(e)}'}), 500

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    stats = dashboard.db.get_statistics()
    return jsonify(stats)

@app.route('/api/assessments/recent')
def recent_assessments():
    """API endpoint for recent assessments"""
    assessments = dashboard.db.get_recent_assessments(10)
    return jsonify(assessments)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for screenplay analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large (max 16MB)'}), 400
        
        # Read file content
        if file.filename.lower().endswith('.txt'):
            content = file.read().decode('utf-8')
        else:
            # For other formats, we'd integrate with a parser
            content = f"# File: {file.filename}\n# Format support coming soon\n\n{file.read().decode('utf-8')}"
        
        writer_info = {
            'name': request.form.get('writer_name', 'Unknown'),
            'email': request.form.get('writer_email', ''),
            'experience': request.form.get('writer_experience', 'unknown')
        }
        
        # Analyze the screenplay
        result = processor.analyze_screenplay(content, writer_info)
        dashboard.db.store_assessment(result)
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f'File {file.filename} analyzed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'File processing failed: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', company="Scene Reader Studio Technologies"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', company="Scene Reader Studio Technologies"), 500

if __name__ == '__main__':
    # Add some sample data for demonstration
    dashboard.add_sample_data()
    dashboard.process_pending_submissions()
    
    print("🚀 Scene Reader Studio Technologies - Web Interface Starting...")
    print("📍 Access the application at: http://localhost:5000")
    print("🎬 AURA Enterprise Platform Ready for Web Access!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)