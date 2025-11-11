"""
Schema normalization module.

This module handles two different JSON schemas from analyzers:
1. Provisional schema (simpler format)
2. Canonical schema (standardized format)

Both get normalized into a common internal format.
"""
from typing import Any, Dict, List


PROVISIONAL_KEYS = ("findings",)
CANONICAL_KEYS = ("results",)


def normalize_findings(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize findings from either provisional or canonical schema.
    
    Returns a list of normalized finding records:
    {
        "type": "unsafe_inline",
        "severity": "high",
        "pre": {...preconditions...}
    }
    """
    if any(k in data for k in PROVISIONAL_KEYS):
        return _from_provisional(data)
    if any(k in data for k in CANONICAL_KEYS):
        return _from_canonical(data)
    raise ValueError("Input does not look like provisional or canonical schema")


def _from_provisional(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert provisional schema to normalized format."""
    out = []
    for f in data.get("findings", []):
        out.append({
            "type": f.get("type", "").strip(),
            "severity": f.get("severity", "info"),
            "pre": f.get("details", {}) or {}
        })
    return out


def _from_canonical(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert canonical schema to normalized format."""
    out = []
    for f in data.get("results", []):
        out.append({
            "type": f.get("type", "").strip(),
            "severity": f.get("severity", "info"),
            "pre": f.get("preconditions", {}) or {}
        })
    return out

