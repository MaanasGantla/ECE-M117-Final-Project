# Runbook — Using the Benign Templates with the Harness

This document explains how to use the generated artifacts with a headless browser harness.

## Inputs
- Snippets in `out/snippets/*.html`
- `out/plan.json` (machine-readable plan)
- `out/catalog.csv` (human-readable index)

## Harness Expectations

### For T-INLINE-1 and T-BLOB-1:
1. Navigate to the target page (e.g., `/account` on the DEMO app).
2. Inject the HTML snippet into the DOM:
   ```javascript
   // Example: inject snippet into page
   document.body.insertAdjacentHTML('beforeend', snippet);
   ```
3. Wait a moment for execution (e.g., 100ms).
4. Assert `window.__PG_MARKER` equals:
   - `'OK'` or `'OK-AUTO'` for T-INLINE-1
   - `'OK-BLOB'` for T-BLOB-1

### For T-TRUSTED-1:
1. **Prerequisite:** Ensure the DEMO host (e.g., `http://assets.demo.local/ok.js`) serves:
   ```javascript
   window.__PG_MARKER = 'OK-TRUSTED';
   ```
   (This is a tiny file that should be hosted on the DEMO CDN.)
2. Navigate to the target page.
3. Inject the snippet.
4. Wait for script to load (e.g., 500ms).
5. Assert either:
   - `window.__PG_MARKER === 'OK-TRUSTED'`, OR
   - `document.body.getAttribute('data-pg-marker') === 'OK-TRUSTED'`

## Evidence Collection

The harness should record:
- Screenshots (optional but useful for demos)
- DOM checks (the marker values)
- Telemetry logs (if a telemetry endpoint is configured)

## Example Playwright/Puppeteer Flow

```javascript
// Pseudocode example
const snippet = fs.readFileSync('out/snippets/T-INLINE-1_unsafe_inline.html', 'utf8');
await page.goto('http://demo-app:3000/account');
await page.evaluate((html) => {
  document.body.insertAdjacentHTML('beforeend', html);
}, snippet);
await page.waitForTimeout(100);
const marker = await page.evaluate(() => window.__PG_MARKER);
assert(marker === 'OK' || marker === 'OK-AUTO');
```

## Notes

- All templates are **benign** - they only set markers, never exfiltrate.
- The `plan.json` file contains structured data you can parse programmatically.
- If telemetry is configured, you can POST marker events to the telemetry URL.
