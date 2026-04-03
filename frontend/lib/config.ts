export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (url) {
    const normalized = url.replace(/\/$/, "");
    // Avoid mixed-content in production: HTTPS frontend should call same-origin
    // `/api/*` and let `app/api/[[...path]]/route.ts` proxy to the HTTP backend.
    // Vercel must set BACKEND_ORIG (or NEXT_PUBLIC_API_BASE_URL) to that API — server-side.
    if (
      typeof window !== "undefined" &&
      window.location.protocol === "https:" &&
      normalized.startsWith("http://")
    ) {
      return "";
    }
    return normalized;
  }
  return "http://localhost:8000";
}
