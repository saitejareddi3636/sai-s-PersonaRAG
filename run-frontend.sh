#!/usr/bin/env bash
# Next.js only (one process). Point API with NEXT_PUBLIC_API_BASE_URL in frontend/.env.local
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$ROOT/frontend/.env.local" ]] || cp "$ROOT/frontend/.env.example" "$ROOT/frontend/.env.local"
cd "$ROOT/frontend"
echo "Frontend: http://127.0.0.1:3000  (Ctrl+C to stop)"
exec npm run dev:light
