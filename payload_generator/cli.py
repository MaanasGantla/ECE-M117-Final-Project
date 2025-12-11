"""Command-line interface for the payload generator."""
import argparse
import json
import yaml
import os
from typing import List

from .generator import PayloadGenerator, GeneratorConfig


def load_yaml(path: str) -> dict:
    """Load a YAML config file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    """Main CLI entry point."""
    p = argparse.ArgumentParser(
        description="Benign CSP template generator (DEMO-only)"
    )
    p.add_argument(
        "--findings",
        required=True,
        help="Path to findings JSON (provisional or canonical)"
    )
    p.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (overrides config)"
    )
    p.add_argument(
        "--config",
        default="config/generator.yaml",
        help="Generator defaults"
    )
    p.add_argument(
        "--allowlist",
        default="config/allowlist.yaml",
        help="Allowed hosts for trusted-host templates"
    )
    p.add_argument(
        "--run-id",
        default="local",
        help="Run identifier for harness correlation"
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Force dry-run true"
    )
    p.add_argument(
        "--this-is-a-demo",
        action="store_true",
        help="Required guard to proceed (acknowledge DEMO-only usage)"
    )
    args = p.parse_args()
    
    # Safety interlock: require explicit acknowledgment
    if not args.this_is_a_demo:
        raise SystemExit(
            "Refusing to run without --this-is-a-demo"
        )
    
    # Load configs
    cfg_yaml = load_yaml(args.config)
    allow = load_yaml(args.allowlist).get("allowed_hosts", [])
    out_dir = args.out_dir or cfg_yaml.get("output_dir", "out")
    
    # Build config object
    cfg = GeneratorConfig(
        out_dir=out_dir,
        # Always default to dry-run for safety
        dry_run=True if (args.dry_run or cfg_yaml.get("dry_run", True)) else True,
        telemetry_url=cfg_yaml.get("telemetry_url", ""),
        allowlist=allow,
        demo_host_fallback=cfg_yaml.get("demo_host_fallback", "")
    )
    
    # Load findings JSON
    with open(args.findings, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Run generator
    g = PayloadGenerator(cfg)
    res = g.generate(data, run_id=args.run_id)
    
    # Print results
    print("Artifacts:")
    for a in res["artifacts"]:
        print("  -", a)
    print("Catalog:", res["catalog"])
    print("Plan   :", res["plan"])


if __name__ == "__main__":
    main()

