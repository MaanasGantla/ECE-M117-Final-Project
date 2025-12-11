import os
import glob
from playwright.sync_api import sync_playwright

def verify_payload(payload, server_url="http://127.0.0.1:5001", csp=None):
    """Verifies a single payload against the mock server."""
    target_url = server_url
    if csp:
        import urllib.parse
        target_url += f"?csp={urllib.parse.quote(csp)}"
        
    result = {"success": False, "marker": None, "error": None}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Navigate to the vulnerable page
            page.goto(target_url)
            page.wait_for_selector("#injection-point", state="attached")
            
            # 2. Inject the payload
            page.evaluate("""(html) => {
                const el = document.getElementById('injection-point');
                if (el) {
                    const range = document.createRange();
                    range.selectNode(el);
                    const fragment = range.createContextualFragment(html);
                    el.innerHTML = '';
                    el.appendChild(fragment);
                } else {
                    throw new Error('Injection point not found');
                }
            }""", payload)
            
            # 3. Wait for the marker
            marker = None
            for _ in range(10): # Try for 2 seconds
                marker = page.evaluate("window.__PG_MARKER")
                if marker:
                    break
                page.wait_for_timeout(200)
            
            if marker:
                result["success"] = True
                result["marker"] = marker
            else:
                result["error"] = "Marker not set"
                
        except Exception as e:
            result["error"] = str(e)
            
        browser.close()
        
    return result

def run_payloads(server_url="http://127.0.0.1:5001"):
    snippet_dir = os.path.join("out", "test_run", "snippets")
    snippets = glob.glob(os.path.join(snippet_dir, "*.html"))
    
    if not snippets:
        print(f"No snippets found in {snippet_dir}")
        return

    print(f"Found {len(snippets)} snippets to test.")

    for snippet_path in snippets:
        snippet_name = os.path.basename(snippet_path)
        print(f"Testing {snippet_name}...", end=" ")
        
        with open(snippet_path, 'r') as f:
            payload = f.read()
        
        res = verify_payload(payload, server_url)
        
        if res["success"]:
            print(f"✅ SUCCESS (Marker: {res['marker']})")
        else:
            print(f"❌ FAILED ({res['error']})")

if __name__ == "__main__":
    run_payloads()
