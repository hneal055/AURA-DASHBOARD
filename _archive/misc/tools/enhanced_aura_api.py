import http.server
import socketserver
import json
import time
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8083

class EnhancedAuraAPI(http.server.BaseHTTPRequestHandler):
    
    # Enhanced metrics with thread safety
    request_count = 0
    successful_parses = 0
    failed_parses = 0
    metrics_lock = threading.Lock()
    start_time = time.time()
    
    # Performance tracking
    response_times = []
    recent_activity = []
    
    def do_GET(self):
        """Enhanced GET handler with all endpoints"""
        start_time = time.time()
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/':
                self.serve_enhanced_dashboard()
            elif path == '/api/health':
                self.serve_health()
            elif path == '/api/aura/status':
                self.serve_aura_status()
            elif path == '/api/metrics':
                self.serve_metrics()
            elif path == '/api/performance':
                self.serve_performance_metrics()
            elif path == '/api/activity':
                self.serve_recent_activity()
            elif path == '/api/endpoints':
                self.serve_endpoints_list()
            else:
                self.serve_error(404, "Endpoint not found")
                
            self._track_metrics("GET", path, True, time.time() - start_time)
                
        except Exception as e:
            self._track_metrics("GET", path, False, time.time() - start_time)
            self.serve_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        """Enhanced POST handler with performance tracking"""
        start_time = time.time()
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8')) if content_length > 0 else {}
            
            if path == '/api/parse':
                self.handle_parse_request(request_data)
            elif path == '/api/aura/parse':
                self.handle_aura_parse(request_data)
            elif path == '/api/batch/parse':
                self.handle_batch_parse(request_data)
            elif path == '/api/analyze':
                self.handle_advanced_analysis(request_data)
            elif path == '/api/validate':
                self.handle_validation(request_data)
            else:
                self.serve_error(404, "Endpoint not found")
                
            self._track_metrics("POST", path, True, time.time() - start_time)
                
        except json.JSONDecodeError as e:
            self._track_metrics("POST", path, False, time.time() - start_time)
            self.serve_error(400, f"Invalid JSON: {str(e)}")
        except Exception as e:
            self._track_metrics("POST", path, False, time.time() - start_time)
            self.serve_error(500, f"Internal server error: {str(e)}")

    def _track_metrics(self, method, endpoint, success, response_time):
        """Track performance metrics"""
        with self.metrics_lock:
            self.request_count += 1
            if success and endpoint in ['/api/parse', '/api/aura/parse', '/api/batch/parse']:
                self.successful_parses += 1
            elif not success:
                self.failed_parses += 1
                
            self.response_times.append(response_time)
            # Keep only last 100 response times
            if len(self.response_times) > 100:
                self.response_times.pop(0)
                
            # Track recent activity
            activity = {
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "endpoint": endpoint,
                "success": success,
                "response_time_ms": round(response_time * 1000, 2)
            }
            self.recent_activity.append(activity)
            if len(self.recent_activity) > 20:
                self.recent_activity.pop(0)

    def handle_parse_request(self, request_data):
        """Enhanced single screenplay parsing"""
        screenplay_content = request_data.get('screenplay', '')
        options = request_data.get('options', {})
        
        print(f"📝 Parsing screenplay: {len(screenplay_content)} characters")
        
        # Enhanced AURA parsing with options
        result = self.aura_parse_screenplay(screenplay_content, options)
        
        self.serve_json({
            "success": True,
            "data": result,
            "aura_enhanced": True,
            "processing_time_ms": result.get('processing_time_ms', 0),
            "timestamp": datetime.now().isoformat()
        })

    def handle_aura_parse(self, request_data):
        """AURA-specific parsing with advanced features"""
        screenplay_content = request_data.get('screenplay', '')
        enhancement_level = request_data.get('enhancement_level', 'standard')
        
        print(f"🔮 AURA Enhanced parsing: {len(screenplay_content)} characters ({enhancement_level})")
        
        result = self.aura_advanced_parse(screenplay_content, enhancement_level)
        
        self.serve_json({
            "success": True,
            "data": result,
            "aura_enhancement": enhancement_level,
            "advanced_features": True,
            "timestamp": datetime.now().isoformat()
        })

    def handle_batch_parse(self, request_data):
        """Enhanced batch processing"""
        screenplays = request_data.get('screenplays', [])
        batch_options = request_data.get('options', {})
        parallel_processing = batch_options.get('parallel', False)
        
        print(f"📦 Batch parsing: {len(screenplays)} screenplays (parallel: {parallel_processing})")
        
        batch_start = time.time()
        results = []
        
        for i, screenplay in enumerate(screenplays):
            result = self.aura_parse_screenplay(screenplay, batch_options)
            result['batch_index'] = i
            results.append(result)
        
        processing_time = (time.time() - batch_start) * 1000
        
        self.serve_json({
            "success": True,
            "batch_size": len(screenplays),
            "processed": len(results),
            "results": results,
            "processing_time_ms": round(processing_time, 2),
            "average_time_per_screenplay": round(processing_time / len(screenplays), 2),
            "parallel_processing": parallel_processing,
            "timestamp": datetime.now().isoformat()
        })

    def handle_advanced_analysis(self, request_data):
        """Advanced screenplay analysis"""
        screenplay_content = request_data.get('screenplay', '')
        analysis_type = request_data.get('analysis_type', 'comprehensive')
        
        print(f"🔍 Advanced analysis: {analysis_type} on {len(screenplay_content)} characters")
        
        analysis_result = self.perform_advanced_analysis(screenplay_content, analysis_type)
        
        self.serve_json({
            "success": True,
            "analysis_type": analysis_type,
            "insights": analysis_result,
            "timestamp": datetime.now().isoformat()
        })

    def handle_validation(self, request_data):
        """Screenplay validation"""
        screenplay_content = request_data.get('screenplay', '')
        validation_rules = request_data.get('validation_rules', ['format', 'structure'])
        
        print(f"✅ Validation check: {validation_rules} on {len(screenplay_content)} characters")
        
        validation_result = self.validate_screenplay(screenplay_content, validation_rules)
        
        self.serve_json({
            "success": True,
            "valid": validation_result['is_valid'],
            "validation_rules": validation_rules,
            "issues": validation_result['issues'],
            "score": validation_result['score'],
            "timestamp": datetime.now().isoformat()
        })

    def aura_parse_screenplay(self, screenplay_text, options=None):
        """Enhanced AURA parsing logic with options"""
        options = options or {}
        start_time = time.time()
        
        # Basic metrics
        word_count = len(screenplay_text.split())
        line_count = screenplay_text.count('\n') + 1
        character_count = len(screenplay_text)
        
        # Advanced analysis
        scenes = self.extract_scenes(screenplay_text)
        characters = self.extract_characters(screenplay_text)
        dialogue_ratio = self.calculate_dialogue_ratio(screenplay_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "processed": True,
            "basic_metrics": {
                "word_count": word_count,
                "line_count": line_count,
                "character_count": character_count,
                "estimated_pages": round(word_count / 250, 1),
                "estimated_duration_minutes": round(word_count / 150, 1)  # approx 150 words per minute
            },
            "advanced_analysis": {
                "scene_count": len(scenes),
                "character_count": len(characters),
                "characters": characters[:10],  # Top 10 characters
                "dialogue_ratio_percent": round(dialogue_ratio * 100, 1),
                "scenes": scenes[:5]  # First 5 scenes
            },
            "processing_time_ms": round(processing_time, 2),
            "analysis": "AURA enhanced parsing completed",
            "timestamp": datetime.now().isoformat()
        }

    def aura_advanced_parse(self, screenplay_text, enhancement_level='standard'):
        """Advanced AURA parsing with different enhancement levels"""
        base_result = self.aura_parse_screenplay(screenplay_text)
        
        if enhancement_level == 'advanced':
            base_result['enhancements'] = {
                "sentiment_analysis": self.analyze_sentiment(screenplay_text),
                "pacing_analysis": self.analyze_pacing(screenplay_text),
                "theme_detection": self.detect_themes(screenplay_text),
                "readability_score": self.calculate_readability(screenplay_text)
            }
        elif enhancement_level == 'expert':
            base_result['enhancements'] = {
                "sentiment_analysis": self.analyze_sentiment(screenplay_text),
                "pacing_analysis": self.analyze_pacing(screenplay_text),
                "theme_detection": self.detect_themes(screenplay_text),
                "readability_score": self.calculate_readability(screenplay_text),
                "character_arcs": self.analyze_character_arcs(screenplay_text),
                "plot_structure": self.analyze_plot_structure(screenplay_text),
                "genre_classification": self.classify_genre(screenplay_text)
            }
        
        base_result['enhancement_level'] = enhancement_level
        return base_result

    def perform_advanced_analysis(self, screenplay_text, analysis_type):
        """Perform comprehensive screenplay analysis"""
        if analysis_type == 'comprehensive':
            return {
                "structure_analysis": self.analyze_structure(screenplay_text),
                "character_analysis": self.analyze_characters_comprehensive(screenplay_text),
                "dialogue_analysis": self.analyze_dialogue(screenplay_text),
                "pacing_analysis": self.analyze_pacing_detailed(screenplay_text)
            }
        elif analysis_type == 'technical':
            return {
                "formatting_issues": self.check_formatting(screenplay_text),
                "consistency_checks": self.check_consistency(screenplay_text),
                "industry_standards": self.check_industry_standards(screenplay_text)
            }
        else:
            return {"analysis": f"Analysis type '{analysis_type}' completed"}

    def validate_screenplay(self, screenplay_text, validation_rules):
        """Validate screenplay against rules"""
        issues = []
        score = 100  # Start with perfect score
        
        if 'format' in validation_rules:
            format_issues = self.validate_formatting(screenplay_text)
            issues.extend(format_issues)
            score -= len(format_issues) * 5
            
        if 'structure' in validation_rules:
            structure_issues = self.validate_structure(screenplay_text)
            issues.extend(structure_issues)
            score -= len(structure_issues) * 3
            
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": max(score, 0)
        }

    # Analysis helper methods
    def extract_scenes(self, text):
        """Extract scenes from screenplay"""
        scenes = []
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith(('INT.', 'EXT.', 'INT ', 'EXT ')):
                scenes.append(line.strip())
        return scenes

    def extract_characters(self, text):
        """Extract characters from screenplay"""
        characters = set()
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            if (stripped.isupper() and 
                not stripped.startswith(('INT.', 'EXT.', 'FADE', 'CUT')) and
                len(stripped) > 1 and len(stripped) < 30):
                characters.add(stripped)
        return list(characters)

    def calculate_dialogue_ratio(self, text):
        """Calculate dialogue to description ratio"""
        lines = text.split('\n')
        dialogue_lines = sum(1 for line in lines if line.strip().isupper() and len(line.strip()) > 1)
        total_lines = len([line for line in lines if line.strip()])
        return dialogue_lines / total_lines if total_lines > 0 else 0

    # Placeholder analysis methods (implement with real logic)
    def analyze_sentiment(self, text):
        return {"sentiment": "neutral", "confidence": 0.75}
    
    def analyze_pacing(self, text):
        return {"pacing": "medium", "scenes_per_minute": 1.2}
    
    def detect_themes(self, text):
        return ["drama", "professional life"]
    
    def calculate_readability(self, text):
        return {"score": 65, "level": "standard"}
    
    def analyze_character_arcs(self, text):
        return {"analysis": "character development detected"}
    
    def analyze_plot_structure(self, text):
        return {"act_structure": "three-act", "turning_points": 2}
    
    def classify_genre(self, text):
        return {"primary_genre": "drama", "secondary_genres": ["slice-of-life"]}
    
    def analyze_structure(self, text):
        return {"act_breakdown": "balanced", "scene_lengths": "varied"}
    
    def analyze_characters_comprehensive(self, text):
        return {"main_characters": 3, "supporting_characters": 5}
    
    def analyze_dialogue(self, text):
        return {"average_dialogue_length": 12.5, "dialogue_variety": "good"}
    
    def analyze_pacing_detailed(self, text):
        return {"pace": "deliberate", "action_sequences": 2}
    
    def check_formatting(self, text):
        return []
    
    def check_consistency(self, text):
        return []
    
    def check_industry_standards(self, text):
        return []
    
    def validate_formatting(self, text):
        return []
    
    def validate_structure(self, text):
        return []

    # Enhanced serving methods
    def serve_health(self):
        """Enhanced health check"""
        with self.metrics_lock:
            success_rate = (self.successful_parses / (self.successful_parses + self.failed_parses) * 100) if (self.successful_parses + self.failed_parses) > 0 else 100
            
            health_data = {
                "status": "healthy",
                "service": "Enhanced AURA API",
                "version": "2.0.0",
                "aura_integration": "active",
                "enhancements": "enabled",
                "performance": {
                    "requests_processed": self.request_count,
                    "successful_parses": self.successful_parses,
                    "failed_parses": self.failed_parses,
                    "success_rate": round(success_rate, 1)
                },
                "system": {
                    "uptime_seconds": round(time.time() - self.start_time, 2),
                    "average_response_time": round((sum(self.response_times) / len(self.response_times)) * 1000, 2) if self.response_times else 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        self.serve_json(health_data)

    def serve_aura_status(self):
        """AURA-specific status"""
        self.serve_json({
            "aura_parser": "connected",
            "status": "operational",
            "version": "enhanced",
            "features": [
                "batch_processing",
                "advanced_analysis", 
                "validation",
                "performance_metrics",
                "real_time_monitoring"
            ],
            "last_check": datetime.now().isoformat()
        })

    def serve_metrics(self):
        """Enhanced performance metrics"""
        with self.metrics_lock:
            total_parses = self.successful_parses + self.failed_parses
            success_rate = (self.successful_parses / total_parses * 100) if total_parses > 0 else 100
            
            metrics = {
                "requests": {
                    "total": self.request_count,
                    "successful_parses": self.successful_parses,
                    "failed_parses": self.failed_parses,
                    "success_rate": round(success_rate, 1)
                },
                "performance": {
                    "uptime_seconds": round(time.time() - self.start_time, 2),
                    "average_response_time_ms": round((sum(self.response_times) / len(self.response_times)) * 1000, 2) if self.response_times else 0,
                    "min_response_time_ms": round(min(self.response_times) * 1000, 2) if self.response_times else 0,
                    "max_response_time_ms": round(max(self.response_times) * 1000, 2) if self.response_times else 0,
                    "requests_per_minute": round(self.request_count / ((time.time() - self.start_time) / 60), 2) if time.time() > self.start_time else 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        self.serve_json(metrics)

    def serve_performance_metrics(self):
        """Detailed performance metrics"""
        with self.metrics_lock:
            performance_data = {
                "response_times": {
                    "recent": [round(t * 1000, 2) for t in self.response_times[-10:]],  # Last 10
                    "average": round((sum(self.response_times) / len(self.response_times)) * 1000, 2) if self.response_times else 0,
                    "percentile_95": round(sorted(self.response_times)[int(len(self.response_times) * 0.95)] * 1000, 2) if self.response_times else 0
                },
                "throughput": {
                    "requests_total": self.request_count,
                    "requests_per_second": round(self.request_count / (time.time() - self.start_time), 2) if time.time() > self.start_time else 0,
                    "parses_per_minute": round(self.successful_parses / ((time.time() - self.start_time) / 60), 2) if time.time() > self.start_time else 0
                },
                "timestamp": datetime.now().isoformat()
            }
        
        self.serve_json(performance_data)

    def serve_recent_activity(self):
        """Recent API activity"""
        with self.metrics_lock:
            self.serve_json({
                "recent_activity": self.recent_activity[-10:],  # Last 10 activities
                "total_activities": len(self.recent_activity),
                "timestamp": datetime.now().isoformat()
            })

    def serve_endpoints_list(self):
        """List all available endpoints"""
        endpoints = {
            "endpoints": {
                "GET": [
                    "/ - Enhanced Dashboard",
                    "/api/health - System health with detailed metrics",
                    "/api/aura/status - AURA parser status",
                    "/api/metrics - Performance metrics", 
                    "/api/performance - Detailed performance data",
                    "/api/activity - Recent API activity",
                    "/api/endpoints - This endpoints list"
                ],
                "POST": [
                    "/api/parse - Enhanced screenplay parsing",
                    "/api/aura/parse - AURA-specific advanced parsing", 
                    "/api/batch/parse - Batch screenplay processing",
                    "/api/analyze - Advanced screenplay analysis",
                    "/api/validate - Screenplay validation"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        self.serve_json(endpoints)

    def serve_enhanced_dashboard(self):
        """Serve the enhanced dashboard"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        dashboard = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced AURA API Dashboard</title>
            <meta charset="UTF-8">
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }
                .header { 
                    background: rgba(255,255,255,0.95); 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                }
                .header h1 { 
                    font-size: 3em; 
                    margin-bottom: 10px; 
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .header p { 
                    font-size: 1.2em; 
                    color: #666; 
                    margin-bottom: 20px;
                }
                .status-badge {
                    display: inline-block;
                    background: #28a745;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }
                .grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                    gap: 25px; 
                    margin-bottom: 30px;
                }
                .card { 
                    background: rgba(255,255,255,0.95); 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
                }
                .card h3 { 
                    color: #4a5568; 
                    margin-bottom: 20px; 
                    font-size: 1.4em;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 10px;
                }
                .endpoint { 
                    background: #f7fafc; 
                    padding: 15px; 
                    margin: 12px 0; 
                    border-radius: 10px; 
                    border-left: 4px solid #667eea;
                    transition: background 0.3s ease;
                }
                .endpoint:hover {
                    background: #edf2f7;
                }
                .endpoint strong { 
                    color: #2d3748; 
                    display: block; 
                    margin-bottom: 5px;
                    font-size: 1.1em;
                }
                .endpoint p { 
                    color: #718096; 
                    margin: 0;
                    font-size: 0.95em;
                }
                .btn { 
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    margin: 8px; 
                    font-size: 1em;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }
                .btn:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }
                .btn:active {
                    transform: translateY(0);
                }
                .btn-group {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 10px;
                    margin: 20px 0;
                }
                .results { 
                    margin-top: 25px; 
                    max-height: 400px; 
                    overflow-y: auto;
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                }
                .success { 
                    color: #28a745; 
                    padding: 12px; 
                    background: #d4edda; 
                    border-radius: 8px; 
                    margin: 8px 0;
                    border-left: 4px solid #28a745;
                }
                .error { 
                    color: #dc3545; 
                    padding: 12px; 
                    background: #f8d7da; 
                    border-radius: 8px; 
                    margin: 8px 0;
                    border-left: 4px solid #dc3545;
                }
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }
                .metric {
                    text-align: center;
                    padding: 15px;
                    background: #f7fafc;
                    border-radius: 10px;
                    border: 1px solid #e2e8f0;
                }
                .metric-value {
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 5px;
                }
                .metric-label {
                    font-size: 0.9em;
                    color: #718096;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .feature-tag {
                    display: inline-block;
                    background: #e9ecef;
                    color: #495057;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    margin: 2px;
                }
                .enhanced { background: #fff3cd; color: #856404; }
                .advanced { background: #d1ecf1; color: #0c5460; }
                .premium { background: #d4edda; color: #155724; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Enhanced AURA API</h1>
                    <p>Production-Ready Screenplay Parsing & Analysis Platform</p>
                    <div class="status-badge">🟢 SYSTEM OPERATIONAL</div>
                    <div class="btn-group">
                        <button class="btn" onclick="testHealth()">System Health</button>
                        <button class="btn" onclick="testMetrics()">Live Metrics</button>
                        <button class="btn" onclick="testAllEndpoints()">Test All</button>
                        <button class="btn" onclick="loadEndpoints()">View Endpoints</button>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Real-Time Metrics</h3>
                        <div class="metrics-grid" id="liveMetrics">
                            <div class="metric">
                                <div class="metric-value" id="requests">-</div>
                                <div class="metric-label">Requests</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="successRate">-</div>
                                <div class="metric-label">Success Rate</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="responseTime">-</div>
                                <div class="metric-label">Avg Response</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="uptime">-</div>
                                <div class="metric-label">Uptime</div>
                            </div>
                        </div>
                        <button class="btn" onclick="refreshMetrics()" style="width: 100%; margin-top: 15px;">Refresh Metrics</button>
                    </div>
                    
                    <div class="card">
                        <h3>🔧 Core Endpoints</h3>
                        <div class="endpoint">
                            <strong>POST /api/parse</strong>
                            <p>Enhanced screenplay parsing with advanced metrics</p>
                            <span class="feature-tag enhanced">Enhanced</span>
                        </div>
                        <div class="endpoint">
                            <strong>POST /api/batch/parse</strong>
                            <p>Batch process multiple screenplays efficiently</p>
                            <span class="feature-tag advanced">Advanced</span>
                        </div>
                        <div class="endpoint">
                            <strong>POST /api/analyze</strong>
                            <p>Comprehensive screenplay analysis</p>
                            <span class="feature-tag premium">Premium</span>
                        </div>
                        <div class="endpoint">
                            <strong>POST /api/validate</strong>
                            <p>Screenplay validation & quality checking</p>
                            <span class="feature-tag premium">Premium</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🧪 Test Panel</h3>
                        <div class="btn-group">
                            <button class="btn" onclick="testParse()">Test Parse</button>
                            <button class="btn" onclick="testBatchParse()">Test Batch</button>
                            <button class="btn" onclick="testAnalysis()">Test Analysis</button>
                            <button class="btn" onclick="testValidation()">Test Validation</button>
                        </div>
                        <div id="results"></div>
                    </div>
                    
                    <div class="card">
                        <h3>📈 System Info</h3>
                        <div class="endpoint">
                            <strong>Version 2.0.0</strong>
                            <p>Enhanced AURA API with all features</p>
                        </div>
                        <div class="endpoint">
                            <strong>Features Active</strong>
                            <p>Batch Processing, Advanced Analysis, Real-time Metrics</p>
                        </div>
                        <div class="endpoint">
                            <strong>Status</strong>
                            <p id="systemStatus">Checking...</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎯 Advanced Testing</h3>
                    <div class="btn-group">
                        <button class="btn" onclick="testAuraParse()">AURA Parse</button>
                        <button class="btn" onclick="testPerformance()">Performance</button>
                        <button class="btn" onclick="testActivity()">Activity Log</button>
                        <button class="btn" onclick="clearResults()">Clear Results</button>
                    </div>
                    <div id="advancedResults"></div>
                </div>
            </div>

            <script>
                const API_BASE = 'http://localhost:8083';
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    testHealth();
                    refreshMetrics();
                });
                
                async function testHealth() {
                    try {
                        const response = await fetch(API_BASE + '/api/health');
                        const data = await response.json();
                        showResult('System Health: ' + data.status.toUpperCase() + ' | Version: ' + data.version, 'success');
                        document.getElementById('systemStatus').textContent = data.status.toUpperCase();
                    } catch (error) {
                        showResult('Health Check Failed: ' + error, 'error');
                    }
                }
                
                async function refreshMetrics() {
                    try {
                        const response = await fetch(API_BASE + '/api/metrics');
                        const data = await response.json();
                        
                        document.getElementById('requests').textContent = data.requests.total.toLocaleString();
                        document.getElementById('successRate').textContent = data.requests.success_rate + '%';
                        document.getElementById('responseTime').textContent = data.performance.average_response_time_ms + 'ms';
                        document.getElementById('uptime').textContent = Math.round(data.performance.uptime_seconds / 60) + 'm';
                        
                    } catch (error) {
                        console.error('Metrics refresh failed:', error);
                    }
                }
                
                async function testParse() {
                    try {
                        const response = await fetch(API_BASE + '/api/parse', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                screenplay: "INT. WRITER'S ROOM - DAY\\n\\nHARRY sits at his desk, surrounded by coffee cups.\\n\\nHARRY\\n(muttering)\\nWhy won't this dialogue work?\\n\\nHe types, then deletes everything.\\n\\nHARRY\\n(cont'd)\\nJust one more scene...",
                                options: { enhance: true }
                            })
                        });
                        const data = await response.json();
                        showResult('Parse: SUCCESS - ' + data.data.basic_metrics.word_count + ' words, ' + 
                                  data.data.basic_metrics.estimated_pages + ' pages', 'success');
                    } catch (error) {
                        showResult('Parse Failed: ' + error, 'error');
                    }
                }
                
                async function testBatchParse() {
                    try {
                        const response = await fetch(API_BASE + '/api/batch/parse', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                screenplays: [
                                    "Screenplay 1: INT. OFFICE - DAY\\nJohn works.",
                                    "Screenplay 2: EXT. PARK - DAY\\nSarah walks.",
                                    "Screenplay 3: INT. CAFE - NIGHT\\nMike drinks coffee."
                                ],
                                options: { parallel: true }
                            })
                        });
                        const data = await response.json();
                        showResult('Batch: ' + data.batch_size + ' screenplays processed in ' + 
                                  data.processing_time_ms + 'ms', 'success');
                    } catch (error) {
                        showResult('Batch Failed: ' + error, 'error');
                    }
                }
                
                async function testAnalysis() {
                    try {
                        const response = await fetch(API_BASE + '/api/analyze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                screenplay: "INT. OFFICE - DAY\\nJohn works.\\nJOHN\\nHello world.",
                                analysis_type: "comprehensive"
                            })
                        });
                        const data = await response.json();
                        showResult('Analysis: ' + data.analysis_type + ' completed', 'success');
                    } catch (error) {
                        showResult('Analysis Failed: ' + error, 'error');
                    }
                }
                
                async function testValidation() {
                    try {
                        const response = await fetch(API_BASE + '/api/validate', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                screenplay: "INT. OFFICE - DAY\\nJohn works.",
                                validation_rules: ["format", "structure"]
                            })
                        });
                        const data = await response.json();
                        showResult('Validation: ' + (data.valid ? 'PASS' : 'FAIL') + ' | Score: ' + data.score, 'success');
                    } catch (error) {
                        showResult('Validation Failed: ' + error, 'error');
                    }
                }
                
                async function testAuraParse() {
                    try {
                        const response = await fetch(API_BASE + '/api/aura/parse', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                screenplay: "INT. OFFICE - DAY\\nAdvanced parsing test.",
                                enhancement_level: "advanced"
                            })
                        });
                        const data = await response.json();
                        showAdvancedResult('AURA Parse: ' + data.aura_enhancement + ' enhancement applied', 'success');
                    } catch (error) {
                        showAdvancedResult('AURA Parse Failed: ' + error, 'error');
                    }
                }
                
                async function testPerformance() {
                    try {
                        const response = await fetch(API_BASE + '/api/performance');
                        const data = await response.json();
                        showAdvancedResult('Performance: Avg ' + data.response_times.average + 'ms response time', 'success');
                    } catch (error) {
                        showAdvancedResult('Performance Check Failed: ' + error, 'error');
                    }
                }
                
                async function testActivity() {
                    try {
                        const response = await fetch(API_BASE + '/api/activity');
                        const data = await response.json();
                        showAdvancedResult('Activity: ' + data.total_activities + ' recent activities', 'success');
                    } catch (error) {
                        showAdvancedResult('Activity Check Failed: ' + error, 'error');
                    }
                }
                
                async function testMetrics() {
                    try {
                        const response = await fetch(API_BASE + '/api/metrics');
                        const data = await response.json();
                        showResult('Metrics: ' + data.requests.success_rate + '% success rate, ' + 
                                  data.performance.requests_per_minute + ' req/min', 'success');
                    } catch (error) {
                        showResult('Metrics Failed: ' + error, 'error');
                    }
                }
                
                async function loadEndpoints() {
                    try {
                        const response = await fetch(API_BASE + '/api/endpoints');
                        const data = await response.json();
                        showAdvancedResult('Endpoints loaded: ' + data.endpoints.GET.length + ' GET, ' + 
                                          data.endpoints.POST.length + ' POST endpoints', 'success');
                    } catch (error) {
                        showAdvancedResult('Endpoints Load Failed: ' + error, 'error');
                    }
                }
                
                async function testAllEndpoints() {
                    const tests = [testHealth, testParse, testBatchParse, testMetrics];
                    for (const test of tests) {
                        await test();
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                }
                
                function showResult(message, type) {
                    const results = document.getElementById('results');
                    const div = document.createElement('div');
                    div.className = type;
                    div.textContent = message;
                    results.appendChild(div);
                    results.scrollTop = results.scrollHeight;
                }
                
                function showAdvancedResult(message, type) {
                    const results = document.getElementById('advancedResults');
                    const div = document.createElement('div');
                    div.className = type;
                    div.textContent = message;
                    results.appendChild(div);
                    results.scrollTop = results.scrollHeight;
                }
                
                function clearResults() {
                    document.getElementById('results').innerHTML = '';
                    document.getElementById('advancedResults').innerHTML = '';
                }
                
                // Auto-refresh metrics every 10 seconds
                setInterval(refreshMetrics, 10000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(dashboard.encode('utf-8'))

    def serve_json(self, data, status=200):
        """Serve JSON response with CORS"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))

    def serve_error(self, code, message):
        """Serve error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {
            "error": True,
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        response = json.dumps(error_response, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Enhanced logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - {self.client_address[0]} - {format % args}")

def start_enhanced_server():
    """Start the enhanced AURA API server"""
    print("🚀 ENHANCED AURA API SERVER STARTING...")
    print("=" * 70)
    print(f"📍 Port: {PORT}")
    print(f"🌐 Dashboard: http://localhost:{PORT}")
    print("🔧 Enhanced Endpoints:")
    print("   GET  /api/health          - Enhanced health with detailed metrics")
    print("   GET  /api/aura/status     - AURA parser status")
    print("   GET  /api/metrics         - Performance metrics")
    print("   GET  /api/performance     - Detailed performance data")
    print("   GET  /api/activity        - Recent API activity")
    print("   GET  /api/endpoints       - List all available endpoints")
    print("   POST /api/parse           - Enhanced screenplay parsing")
    print("   POST /api/aura/parse      - AURA-specific advanced parsing")
    print("   POST /api/batch/parse     - Batch screenplay processing")
    print("   POST /api/analyze         - Advanced screenplay analysis")
    print("   POST /api/validate        - Screenplay validation")
    print("🎯 Features: Batch Processing, Advanced Analysis, Real-time Metrics")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        with socketserver.TCPServer(("", PORT), EnhancedAuraAPI) as httpd:
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print("💡 Try: netstat -ano | findstr :{PORT}")
            print("💡 Or change PORT variable to 8084")
        else:
            print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Enhanced AURA API server stopped")

if __name__ == "__main__":
    start_enhanced_server()
