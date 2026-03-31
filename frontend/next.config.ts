import type { NextConfig } from "next";

const backendOrigin =
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim().replace(/\/$/, "") ||
  "http://159.54.172.124:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendOrigin}/api/:path*`,
      },
      {
        source: "/outputs/:path*",
        destination: `${backendOrigin}/outputs/:path*`,
      },
    ];
  },
};

export default nextConfig;
