# Finding Schema Mapping

The generator accepts both a provisional schema and a canonical schema format.

## Provisional (accepted now)
```json
{
  "findings": [
    { "type": "unsafe_inline", "severity": "high", "details": {} },
    { "type": "blob_allowed", "severity": "med", "details": {} },
    { "type": "trusted_host_wildcard",
      "severity": "high",
      "details": { "allowed_hosts": ["https://*.demo.local"] }
    }
  ]
}
```

## Canonical (Standardized format)
```json
{
  "meta": { "scanned_url": "..." },
  "results": [
    {
      "id": "CSP-001",
      "category": "script-src",
      "type": "unsafe-inline",
      "severity": "high",
      "evidence": { "directive": "script-src", "raw": "..." },
      "preconditions": {}
    }
  ]
}
```

## Mapping Rules

The generator normalizes both schemas internally. Key mappings:

- `unsafe_inline` or `unsafe-inline` → **T-INLINE-1**
- `blob_allowed` or `data_allowed` → **T-BLOB-1**
- `trusted_host_wildcard` or `trusted_host_overbroad` → **T-TRUSTED-1**

## Implementation Notes

When implementing an analyzer that outputs findings for this generator, please ensure:
1. The `type` field uses one of the keys listed in `FINDING_TO_TEMPLATE` (see `payload_generator/mappings.py`)
2. Preconditions (if any) go in the `preconditions` field (canonical) or `details` field (provisional)
3. See `samples/findings.canonical.json` for the exact expected format

