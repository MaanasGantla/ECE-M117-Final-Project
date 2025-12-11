import unittest
import os
import shutil
from payload_generator.generator import PayloadGenerator, GeneratorConfig

class TestPayloadGeneratorFix(unittest.TestCase):
    def setUp(self):
        self.out_dir = "test_out"
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)
            
        self.cfg = GeneratorConfig(
            out_dir=self.out_dir,
            dry_run=False,
            telemetry_url="http://localhost:3000",
            allowlist=["example.com"],
            demo_host_fallback="example.com"
        )
        self.generator = PayloadGenerator(self.cfg)

    def tearDown(self):
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)

    def test_report_only_payload_generation(self):
        # Simulate findings from csp_analyzer for a Report-Only case
        findings = {
            "findings": [
                {
                    "type": "csp_report_only",
                    "severity": "med",
                    "details": {
                        "message": "Enforced CSP is missing, but Report-Only header was found.",
                        "raw": "script-src 'unsafe-inline'"
                    }
                },
                {
                    "type": "unsafe_inline (Report-Only)",
                    "severity": "info",
                    "details": {
                        "directive": "script-src",
                        "raw": "script-src 'unsafe-inline'"
                    }
                }
            ]
        }

        # Run generator
        result = self.generator.generate(findings, run_id="test_run")
        
        # Verify artifacts were generated
        self.assertTrue(len(result["artifacts"]) > 0, "Should generate artifacts")
        
        # Check if specific templates were used
        snippets_dir = os.path.join(self.out_dir, "snippets")
        files = os.listdir(snippets_dir)
        print(f"Generated files: {files}")
        

        
        self.assertIn("T-INLINE-1_csp_report_only.html", files)
        self.assertIn("T-INLINE-1_unsafe_inline (Report-Only).html", files)

if __name__ == '__main__':
    unittest.main()
