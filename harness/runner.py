import os
import glob
from playwright.sync_api import sync_playwright

def run_payloads(server_url="http://127.0.0.1:5000"):
    snippet_dir = os.path.join("out", "test_run", "snippets")
    snippets = glob.glob(os.path.join(snippet_dir, "*.html"))
    
    if not snippets:
        print(f"No snippets found in {snippet_dir}")
        return

    print(f"Found {len(snippets)} snippets to test.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Debug: Log network requests
        page.on("requestfailed", lambda request: print(f"❌ Request failed: {request.url} - {request.failure}"))
        page.on("requestfinished", lambda request: print(f"✅ Request finished: {request.url}"))
        page.on("console", lambda msg: print(f"📜 Console: {msg.text}"))
        
        for snippet_path in snippets:
            snippet_name = os.path.basename(snippet_path)
            print(f"Testing {snippet_name}...", end=" ")
            
            with open(snippet_path, 'r') as f:
                payload = f.read()
            
            try:
                # 1. Navigate to the vulnerable page
                page.goto(server_url)
                page.wait_for_selector("#injection-point", state="attached")
                
                # 2. Inject the payload
                # We simulate an XSS by injecting the HTML directly into the DOM
                page.evaluate("""(html) => {
                    const el = document.getElementById('injection-point');
                    if (el) {
                        // Use createContextualFragment to ensure scripts execute
                        const range = document.createRange();
                        range.selectNode(el);
                        const fragment = range.createContextualFragment(html);
                        el.innerHTML = ''; // Clear previous content
                        el.appendChild(fragment);
                    } else {
                        throw new Error('Injection point not found');
                    }
                }""", payload)
                
                # 3. Wait for the marker
                # The payloads set window.__PG_MARKER
                marker = None
                for _ in range(10): # Try for 2 seconds (10 * 0.2s)
                    marker = page.evaluate("window.__PG_MARKER")
                    if marker:
                        break
                    page.wait_for_timeout(200)
                
                if marker:
                    print(f"✅ SUCCESS (Marker: {marker})")
                else:
                    print(f"❌ FAILED (Marker not set)")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                # Debug: print page content if something goes wrong
                try:
                    print("DEBUG: Page Content:")
                    print(page.content())
                except:
                    pass
                
        browser.close()

if __name__ == "__main__":
    run_payloads()
