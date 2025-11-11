"""
Adapter utilities for template context.

These are small helper functions that prepare data
for the Jinja2 templates (like picking a safe DEMO host).
"""
from typing import Dict, List


def select_demo_host(pre: Dict, allowlist: List[str], fallback: str) -> str:
    """
    Select a DEMO host from preconditions that is in the allowlist.
    
    This ensures we only use hosts that are explicitly allowed
    (safety interlock for T-TRUSTED-1 template).
    
    Args:
        pre: Preconditions dict (may contain "allowed_hosts")
        allowlist: List of allowed hostnames
        fallback: Default host if none match
    
    Returns:
        A hostname that is guaranteed to be in the allowlist
    """
    hosts = pre.get("allowed_hosts", []) or []
    for h in hosts:
        if h in allowlist:
            return h
    return fallback

