# Frontend

Next.js (TypeScript, Tailwind). The UI talks to the FastAPI backend at `POST /api/chat`.

## Setup

```bash
npm install
cp .env.example .env.local
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if the API is not on `http://localhost:8000`.

```bash
npm run dev
```

See the repository root [README](../README.md) for monorepo context.
