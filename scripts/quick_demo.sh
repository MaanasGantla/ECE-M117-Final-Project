#!/usr/bin/env bash
set -euo pipefail

# Quick demo script to test the payload generator
# This runs the generator on the provisional sample findings

python -m payload_generator.cli \
  --findings samples/findings.provisional.json \
  --this-is-a-demo