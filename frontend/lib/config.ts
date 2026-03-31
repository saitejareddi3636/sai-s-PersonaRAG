export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (url) {
    const normalized = url.replace(/\/$/, "");
    // Avoid mixed-content in production: HTTPS frontend should call same-origin
    // and let Next.js rewrites proxy to the HTTP backend.
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
