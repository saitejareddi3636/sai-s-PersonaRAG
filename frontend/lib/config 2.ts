export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (url) return url.replace(/\/$/, "");
  return "http://localhost:8000";
}
