import requests
import json
from urllib.parse import urlparse

def fetch_csp(url):
    """Fetches the CSP headers from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        return {
            "enforced": response.headers.get('Content-Security-Policy'),
            "report_only": response.headers.get('Content-Security-Policy-Report-Only')
        }
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
    if not csp_string:
        return {"findings": []}
        
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
    csp_headers = fetch_csp(url)
    if not csp_headers:
        return {"findings": [{"type": "error", "severity": "high", "details": {"message": "Failed to fetch URL"}}]}
        
    enforced = csp_headers.get("enforced")
    report_only = csp_headers.get("report_only")
    
    findings = []
    
    # Check for missing enforced CSP
    if not enforced:
        if report_only:
            findings.append({
                "type": "csp_report_only",
                "severity": "med",
                "details": {
                    "message": "Enforced CSP is missing, but Report-Only header was found.",
                    "raw": report_only
                }
            })
            # Analyze the report-only policy too, just to show what it would catch
            ro_analysis = analyze_csp(report_only, url)
            for f in ro_analysis["findings"]:
                f["type"] += " (Report-Only)"
                f["severity"] = "info" # Downgrade severity for report-only
                findings.append(f)
        else:
            findings.append({
                "type": "missing_csp",
                "severity": "high",
                "details": {
                    "message": "No Content-Security-Policy header found. This allows all content sources."
                }
            })
            
    # Analyze enforced CSP if present
    if enforced:
        analysis_result = analyze_csp(enforced, url)
        findings.extend(analysis_result["findings"])
    
    return {
        "csp": enforced or report_only, # Return whichever exists for visualization
        "findings": findings
    }
