# CSP Payload Generator

## Payload Generator (Benign, DEMO-Only)

A benign exploit generator that produces safe HTML snippets to test CSP weaknesses in a controlled DEMO environment. All templates are non-exfiltrating and only set harmless markers.

### Quick Start

1. **Install dependencies:**
   ```bash
   python -m pip install jinja2 pyyaml
   ```

2. **Run the demo:**
   ```bash
   chmod +x scripts/quick_demo.sh
   ./scripts/quick_demo.sh
   ```
   
   Or manually:
   ```bash
   python -m payload_generator.cli \
     --findings samples/findings.provisional.json \
     --this-is-a-demo
   ```

3. **Check outputs:**
   - `./out/snippets/*.html` - The benign HTML snippets
   - `./out/catalog.csv` - Index of templates
   - `./out/plan.json` - Machine-readable plan for harness

### CSP Analyzer

You can also analyze a live URL to generate findings:

```bash
python -m csp_analyzer.cli --url https://example.com --out findings.json
```

Then feed the findings into the generator:

```bash
python -m payload_generator.cli --findings findings.json --this-is-a-demo
```
```bash
python -m payload_generator.cli --findings findings.json --this-is-a-demo
```

### Harness (Verification)

To verify that the generated payloads actually work, you can run the harness. This spins up a mock vulnerable server and uses a headless browser to inject the payloads.

```bash
# Install additional dependencies
python -m pip install flask playwright
playwright install

# Run the full test suite (Analyzer -> Generator -> Harness)
./scripts/test_all.sh
```

### Web GUI

For a visual experience, run the web dashboard:

```bash
python -m gui.app
```
Then open [http://localhost:8080](http://localhost:8080) in your browser.

### Safety Features

- Generator emits only benign markers (no exfiltration)
- Refuses non-allowlisted hosts (strict allowlist enforcement)
- Defaults to dry-run mode
- Requires explicit `--this-is-a-demo` flag

### Project Structure

```
.
├── payload_generator/     # Main generator package
│   ├── cli.py             # Command-line interface
│   ├── generator.py       # Core generation logic
│   ├── schema.py          # Schema normalization (provisional ↔ canonical)
│   ├── mappings.py        # Finding type → template mapping
│   ├── adapters.py        # Helper utilities
│   └── templates/         # Jinja2 template files
├── config/                # Configuration files
│   ├── allowlist.yaml     # Allowed hosts (safety)
│   └── generator.yaml     # Default settings
├── samples/               # Sample findings JSON
│   ├── findings.provisional.json
│   └── findings.canonical.json
├── docs/                  # Documentation
│   ├── templates_spec.md  # Template catalog & assertions
│   ├── schema_mapping.md  # Schema documentation
│   └── runbook.md         # Integration instructions
└── scripts/
    └── quick_demo.sh      # One-command demo
```
### Usage

```bash
python -m payload_generator.cli \
  --findings <path-to-findings.json> \
  --this-is-a-demo \
  [--out-dir out] \
  [--run-id local] \
  [--config config/generator.yaml] \
  [--allowlist config/allowlist.yaml]
```

### Template Types

- **T-INLINE-1**: For `unsafe-inline` findings → sets `window.__PG_MARKER`
- **T-BLOB-1**: For `blob_allowed`/`data_allowed` → creates Blob URL script
- **T-TRUSTED-1**: For `trusted_host_wildcard` → loads script from allowlisted DEMO host

See `docs/templates_spec.md` for full details.

---

**Note:** This generator is designed for DEMO/testing environments only. All templates are benign and do not exfiltrate data.
