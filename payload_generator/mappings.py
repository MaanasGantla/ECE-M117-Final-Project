"""
Mapping rules: finding types → template IDs.

This is the "rulebook" that determines which template to use
for each type of CSP weakness found by the analyzer.
"""
from typing import Dict


# Map finding.type → template ID
# This is the core logic: "if we see X weakness, use Y template"
FINDING_TO_TEMPLATE = {
    # Inline script weaknesses
    "unsafe-inline": "T-INLINE-1",
    "unsafe_inline": "T-INLINE-1",
    "missing_csp": "T-INLINE-1",
    
    # Blob/data URL weaknesses
    "blob_allowed": "T-BLOB-1",
    "data_allowed": "T-BLOB-1",
    
    # Trusted host weaknesses
    "trusted_host_wildcard": "T-TRUSTED-1",
    "trusted_host_overbroad": "T-TRUSTED-1",
}


# Map template ID → Jinja2 template file name
TEMPLATE_FILES = {
    "T-INLINE-1": "inline_marker.html.j2",
    "T-BLOB-1": "blob_marker.html.j2",
    "T-TRUSTED-1": "trusted_host_script.html.j2",
}


# Human-readable descriptions (for catalog.csv)
DESCRIPTIONS = {
    "T-INLINE-1": "Inline script marker (benign)",
    "T-BLOB-1": "Blob/data URL marker (benign)",
    "T-TRUSTED-1": "Trusted-host DEMO script marker (benign)",
}

