import unittest
from unittest.mock import patch, MagicMock
from csp_analyzer.analyzer import run_analysis

class TestCSPAnalyzer(unittest.TestCase):
    
    @patch('csp_analyzer.analyzer.requests.get')
    def test_unsafe_inline(self, mock_get):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Security-Policy': "script-src 'self' 'unsafe-inline'"}
        mock_get.return_value = mock_response
        
        result = run_analysis("http://example.com")
        findings = result['findings']
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'unsafe_inline')

    @patch('csp_analyzer.analyzer.requests.get')
    def test_blob_allowed(self, mock_get):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Security-Policy': "script-src 'self' blob:"}
        mock_get.return_value = mock_response
        
        result = run_analysis("http://example.com")
        findings = result['findings']
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'blob_allowed')

    @patch('csp_analyzer.analyzer.requests.get')
    def test_wildcard(self, mock_get):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Security-Policy': "script-src 'self' https://*.example.com"}
        mock_get.return_value = mock_response
        
        result = run_analysis("http://example.com")
        findings = result['findings']
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'trusted_host_wildcard')
        self.assertIn("https://*.example.com", findings[0]['details']['allowed_hosts'])

if __name__ == '__main__':
    unittest.main()
