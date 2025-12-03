import unittest
from unittest.mock import patch, MagicMock
from csp_analyzer.analyzer import run_analysis

class TestAnalyzerFix(unittest.TestCase):
    @patch('csp_analyzer.analyzer.requests.get')
    def test_run_analysis_with_unsafe_inline(self, mock_get):
        # Mock response with a CSP header containing 'unsafe-inline'
        mock_response = MagicMock()
        mock_response.headers = {'Content-Security-Policy': "script-src 'unsafe-inline' 'self'; object-src 'none';"}
        mock_get.return_value = mock_response

        # Run analysis
        result = run_analysis("http://example.com")

        # Verify findings
        self.assertIn("findings", result)
        findings = result["findings"]
        self.assertTrue(len(findings) > 0)
        
        # Check for specific finding
        unsafe_inline_found = any(f["type"] == "unsafe_inline" for f in findings)
        self.assertTrue(unsafe_inline_found, "Should detect 'unsafe-inline'")
        
        print("Verification successful: 'unsafe-inline' detected.")

if __name__ == '__main__':
    unittest.main()
