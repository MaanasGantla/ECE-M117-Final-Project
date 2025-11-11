#!/usr/bin/env bash
set -euo pipefail

CSP_PROFILE="${1:-baseline}"

echo "[runner] Starting containers (CSP_PROFILE=$CSP_PROFILE) ..."
export CSP_PROFILE
docker compose down -v --remove-orphans >/dev/null 2>&1 || true
docker compose build --no-cache demo
docker compose up -d

echo "[runner] Installing harness deps ..."
pushd harness >/dev/null
npm ci --ignore-scripts
npm run prepare
popd >/dev/null

echo "[runner] Running harness against generator outputs in ../sample_out ..."
BASE_URL="http://localhost:3000/" OUT_DIR="${OUT_DIR:-./sample_out}" node harness/tests/run.js
