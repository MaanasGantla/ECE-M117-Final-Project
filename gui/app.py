import os
import json
import tempfile
from flask import Flask, render_template, request, jsonify
from csp_analyzer.analyzer import run_analysis
from payload_generator.generator import PayloadGenerator, GeneratorConfig

app = Flask(__name__)

# Configuration
OUT_DIR = os.path.join(os.getcwd(), "out", "gui_run")
ALLOWLIST_PATH = os.path.join(os.getcwd(), "config", "allowlist.yaml")

def load_allowlist():
    import yaml
    with open(ALLOWLIST_PATH, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('allowed_hosts', [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Run Analyzer
        results = run_analysis(url)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    findings = data.get('findings')
    if not findings:
        return jsonify({"error": "Findings are required"}), 400
    
    try:
        # Configure Generator
        allowlist = load_allowlist()
        cfg = GeneratorConfig(
            out_dir=OUT_DIR,
            dry_run=True,
            telemetry_url="http://localhost/telemetry",
            allowlist=allowlist,
            demo_host_fallback="https://assets.demo.local"
        )
        gen = PayloadGenerator(cfg)
        
        # Run Generator
        # Wrap findings in expected structure if not already
        if "findings" not in findings and isinstance(findings, list):
             findings = {"findings": findings}
             
        result = gen.generate(findings, run_id="gui")
        
        # Read generated snippets to return them
        snippets = []
        for artifact_path in result['artifacts']:
            filename = os.path.basename(artifact_path)
            with open(artifact_path, 'r') as f:
                content = f.read()
            snippets.append({
                "name": filename,
                "content": content
            })
            
        return jsonify({"snippets": snippets})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    payload = data.get('payload')
    csp = data.get('csp')
    
    if not payload:
        return jsonify({"error": "Payload is required"}), 400
        
    try:
        # Ensure mock server is running
        # For this demo, we assume the mock server is running on port 5000
        # or we could start it here. To keep it simple, we'll try to connect,
        # and if it fails, we'll try to start it.
        import requests
        try:
            requests.get("http://127.0.0.1:5000", timeout=1)
        except requests.ConnectionError:
            # Start mock server in background
            import subprocess
            import sys
            subprocess.Popen([sys.executable, "harness/mock_server.py"])
            import time
            time.sleep(2) # Wait for startup
            
        from harness.runner import verify_payload
        result = verify_payload(payload, csp=csp)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080, debug=True)
