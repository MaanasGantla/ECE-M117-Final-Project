"""
Main payload generator engine.

This is the "production line" that:
1. Takes normalized findings
2. Maps them to templates
3. Renders Jinja2 templates
4. Writes output files (snippets, catalog, plan)
"""
import json
import csv
import os
import pathlib
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schema import normalize_findings
from .mappings import FINDING_TO_TEMPLATE, TEMPLATE_FILES, DESCRIPTIONS
from .adapters import select_demo_host


class GeneratorConfig:
    """Configuration for the generator."""
    def __init__(
        self,
        out_dir: str,
        dry_run: bool,
        telemetry_url: str,
        allowlist: List[str],
        demo_host_fallback: str
    ):
        self.out_dir = out_dir
        self.dry_run = dry_run
        self.telemetry_url = telemetry_url
        self.allowlist = allowlist
        self.demo_host_fallback = demo_host_fallback


class PayloadGenerator:
    """Main generator class that produces benign templates."""
    
    def __init__(self, cfg: GeneratorConfig):
        self.cfg = cfg
        # Set up Jinja2 environment to load templates
        tmpl_dir = pathlib.Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(tmpl_dir)),
            autoescape=select_autoescape(enabled_extensions=('html',))
        )
    
    def generate(self, findings_json: Dict[str, Any], run_id: str = "local") -> Dict[str, Any]:
        """
        Generate benign templates from findings.
        
        Args:
            findings_json: Raw JSON from analyzer (provisional or canonical)
            run_id: Identifier for this run (for harness correlation)
        
        Returns:
            Dict with paths to generated artifacts
        """
        # Normalize findings (handles both schemas)
        normalized = normalize_findings(findings_json)
        
        plan: List[Dict[str, Any]] = []
        artifacts: List[str] = []
        catalog_rows: List[List[str]] = []
        
        # Create output directories
        os.makedirs(self.cfg.out_dir, exist_ok=True)
        out_snippets_dir = os.path.join(self.cfg.out_dir, "snippets")
        os.makedirs(out_snippets_dir, exist_ok=True)
        
        # Process each finding
        for f in normalized:
            ftype = f["type"]
            # Look up which template to use
            t_id = FINDING_TO_TEMPLATE.get(ftype)
            if not t_id:
                # Unknown finding type → skip
                continue
            
            # Get the Jinja2 template
            j2file = TEMPLATE_FILES[t_id]
            template = self.env.get_template(j2file)
            
            # Prepare template context (variables for Jinja2)
            if t_id == "T-TRUSTED-1":
                # For trusted host templates, we need to pick a safe DEMO host
                demo_host = select_demo_host(
                    f["pre"],
                    self.cfg.allowlist,
                    self.cfg.demo_host_fallback
                )
                # Safety check: refuse if host not in allowlist
                if demo_host not in self.cfg.allowlist:
                    raise RuntimeError(
                        f"Refusing to emit {t_id} for non-allowed host: {demo_host}"
                    )
                ctx = {
                    "demo_host": demo_host,
                    "telemetry_url": self.cfg.telemetry_url,
                    "run_id": run_id
                }
            else:
                # For other templates, simpler context
                ctx = {
                    "telemetry_url": self.cfg.telemetry_url,
                    "run_id": run_id
                }
            
            # Render template to HTML
            rendered = template.render(**ctx)
            
            # Write snippet file
            out_name = f"{t_id}_{ftype}.html"
            out_path = os.path.join(out_snippets_dir, out_name)
            with open(out_path, "w", encoding="utf-8") as f_out:
                f_out.write(rendered)
            artifacts.append(out_path)
            
            # Add to catalog
            catalog_rows.append([
                t_id,
                ftype,
                DESCRIPTIONS[t_id],
                out_name
            ])
            
            # Add to plan (for harness)
            plan.append({
                "finding_type": ftype,
                "template_id": t_id,
                "artifact": out_path,
                "assertion": "Check window.__PG_MARKER or data-pg-marker attribute"
            })
        
        # Write catalog.csv (human-readable index)
        catalog_path = os.path.join(self.cfg.out_dir, "catalog.csv")
        with open(catalog_path, "w", newline="", encoding="utf-8") as cf:
            w = csv.writer(cf)
            w.writerow(["template_id", "finding_type", "description", "artifact"])
            w.writerows(catalog_rows)
        
        # Write plan.json (machine-readable for harness)
        plan_path = os.path.join(self.cfg.out_dir, "plan.json")
        with open(plan_path, "w", encoding="utf-8") as pf:
            json.dump({
                "run_id": run_id,
                "items": plan
            }, pf, indent=2)
        
        return {
            "artifacts": artifacts,
            "catalog": catalog_path,
            "plan": plan_path
        }

