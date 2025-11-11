# Benign Template Catalog (for DEMO only)

Each template is **non-exfiltrating** and exists to create a **local marker** observable by the harness or telemetry server. All templates require the harness to inject or host in a controlled DEMO environment.

## Template IDs

### T-INLINE-1 (Inline Marker)
**Applies when:** finding.type in { `unsafe_inline`, `unsafe-inline` }  
**Preconditions:** `script-src` permits inline or event handlers.  
**Action (benign):** sets `window.__PG_MARKER = 'OK'` or `'OK-AUTO'`.  
**Assertion:** harness checks `window.__PG_MARKER === 'OK'` or `'OK-AUTO'`.

### T-BLOB-1 (Blob Script Marker)
**Applies when:** finding.type in { `blob_allowed`, `data_allowed` }  
**Preconditions:** `script-src` permits `blob:` or `data:`.  
**Action (benign):** creates a Blob URL for a tiny script that sets `window.__PG_MARKER = 'OK-BLOB'`.  
**Assertion:** harness checks `window.__PG_MARKER === 'OK-BLOB'`.

### T-TRUSTED-1 (Trusted Host Script – DEMO Host Only)
**Applies when:** finding.type in { `trusted_host_wildcard`, `trusted_host_overbroad` }  
**Preconditions:** `script-src` allows a host present in `config/allowlist.yaml`.  
**Action (benign):** loads `/ok.js` from a **DEMO** host; script only writes `window.__PG_MARKER = 'OK-TRUSTED'`.  
**Assertion:** harness checks `window.__PG_MARKER === 'OK-TRUSTED'` or `document.body.getAttribute('data-pg-marker') === 'OK-TRUSTED'`.

## Safety Interlocks
- Generator **refuses** to emit T-TRUSTED-1 unless the host is in `allowlist.yaml`.
- Generator defaults to `--dry-run true`.
- Templates never contain exfiltration endpoints.
- All markers are benign and only observable within the DEMO environment.

