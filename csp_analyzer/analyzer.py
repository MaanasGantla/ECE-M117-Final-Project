import requests
import json
from urllib.parse import urlparse

def fetch_csp(url):
    """Fetches the CSP header from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        csp_header = response.headers.get('Content-Security-Policy')
        if not csp_header:
            print(f"No CSP header found for {url}")
            return None
        return csp_header
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_csp(csp_string):
    """Parses a CSP string into a dictionary of directives."""
    directives = {}
    if not csp_string:
        return directives
    
    parts = csp_string.split(';')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        if not tokens:
            continue
        directive_name = tokens[0]
        values = tokens[1:]
        directives[directive_name] = values
    return directives

def analyze_csp(csp_string, url):
    """Analyzes the CSP string for vulnerabilities."""
    directives = parse_csp(csp_string)
    findings = []
    
    script_src = directives.get('script-src', [])
    # Also check default-src if script-src is missing, but for this demo we focus on script-src
    
    # Check for unsafe-inline
    if "'unsafe-inline'" in script_src:
        findings.append({
            "type": "unsafe_inline",
            "severity": "high",
            "details": {
                "directive": "script-src",
                "raw": csp_string
            }
        })
        
    # Check for blob: or data:
    if "blob:" in script_src or "data:" in script_src:
        findings.append({
            "type": "blob_allowed",
            "severity": "med",
            "details": {
                "directive": "script-src",
                "schemes": [s for s in script_src if s in ["blob:", "data:"]]
            }
        })
        
    # Check for wildcards or broad domains (simplified check)
    wildcards = [h for h in script_src if "*" in h and h not in ["'unsafe-inline'", "'unsafe-eval'", "'self'", "'none'"]]
    if wildcards:
        findings.append({
            "type": "trusted_host_wildcard",
            "severity": "high",
            "details": {
                "allowed_hosts": wildcards
            }
        })
        
    return {
        "findings": findings
    }

def run_analysis(url):
    """Runs the full analysis pipeline."""
    csp = fetch_csp(url)
    if not csp:
        # Missing CSP is a high severity finding
        return {
            "findings": [{
                "type": "missing_csp",
                "severity": "high",
                "details": {
                    "message": "No Content-Security-Policy header found. This allows all content sources."
                }
            }]
        }
    
    return analyze_csp(csp, url)
