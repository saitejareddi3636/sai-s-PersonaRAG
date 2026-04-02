import type { NextConfig } from "next";

/**
 * Server-side rewrite target (Vercel → your API). Set in Vercel to your OCI public URL,
 * e.g. http://YOUR_PUBLIC_IP:8000 or https://api.yourdomain.com
 * (must be reachable from Vercel’s build / request handling).
 */
const backendOrigin =
  process.env.BACKEND_ORIG?.trim().replace(/\/$/, "") ||
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim().replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // /api/* is handled by app/api/[[...path]]/route.ts (Node, long maxDuration on Vercel).
      {
        source: "/outputs/:path*",
        destination: `${backendOrigin}/outputs/:path*`,
      },
    ];
  },
};

export default nextConfig;
