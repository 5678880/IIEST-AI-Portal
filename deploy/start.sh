#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8001}"
export PORT="${PORT:-8501}"

cd "$ROOT_DIR/assesment_backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

cd "$ROOT_DIR/assessment_frontend"
python -m streamlit run app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
