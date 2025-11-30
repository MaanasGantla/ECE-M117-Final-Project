#!/bin/bash
set -e

# Resolve the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Assuming the script is in /scripts, the project root is one level up
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"
echo "Changed directory to project root: $PROJECT_ROOT"

# 0. Install Dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 1. Run Unit Tests
echo "Running Unit Tests..."
if [ -f verify_analyzer.py ]; then
    python3 verify_analyzer.py
else
    echo "verify_analyzer.py not found, skipping unit tests."
fi

# 2. Run Analyzer (Mocked or Real)
# Since we don't have a guaranteed live site with specific vulnerabilities, 
# we'll use the sample findings for the generator test, but we can dry-run the analyzer.
echo "Running Analyzer (Dry Run)..."
python3 -m csp_analyzer.cli --url https://google.com --out out/google_findings.json

# 3. Run Generator with Sample Findings
echo "Running Generator..."
python3 -m payload_generator.cli \
  --findings samples/findings.provisional.json \
  --this-is-a-demo \
  --out-dir out/test_run

echo "------------------------------------------------"
echo "✅ Test Complete!"
echo "Analyzer output: out/google_findings.json"
echo "Generator output: out/test_run/"
