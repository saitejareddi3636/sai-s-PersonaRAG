#!/usr/bin/env bash
# One-time: Python venv, pip deps, npm deps, env files. Run from repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
[[ -f .env ]] || cp .env.example .env
cd "$ROOT/frontend"
npm install
[[ -f .env.local ]] || cp .env.example .env.local
echo ""
echo "Setup done. Start the app with:  ./run.sh"
echo "Then open http://localhost:3000  (API: http://127.0.0.1:8000/health)"
