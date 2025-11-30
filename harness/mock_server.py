from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/')
def index():
    # Allow CSP to be overridden via query param for the sandbox
    csp = request.args.get('csp')
    if not csp:
        # Default vulnerable CSP for demo purposes
        csp = "script-src 'self' 'unsafe-inline' blob: data: https://*.demo.local http://127.0.0.1:5000"
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Demo Page</title>
    </head>
    <body>
        <h1>Vulnerable Demo Page</h1>
        <p>This page simulates a vulnerable application.</p>
        <div id="injection-point"></div>
    </body>
    </html>
    """
    response = make_response(html)
    response.headers['Content-Security-Policy'] = csp
    return response

@app.route('/ok.js')
def ok_js():
    return "window.__PG_MARKER = 'OK-TRUSTED';"

if __name__ == '__main__':
    app.run(port=5000)
