"""Adapter utilities for template context."""
from typing import Dict, List


def select_demo_host(pre: Dict, allowlist: List[str], fallback: str) -> str:
    """Select a DEMO host from preconditions that is in the allowlist."""
    hosts = pre.get("allowed_hosts", []) or []
    for h in hosts:
        if h in allowlist:
            return h
    return fallback

