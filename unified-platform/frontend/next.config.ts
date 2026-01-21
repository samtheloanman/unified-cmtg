import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  trailingSlash: false,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.INTERNAL_API_URL
          ? `${process.env.INTERNAL_API_URL}/api/:path*`
          : 'http://127.0.0.1:8001/api/:path*',
      },
      {
        source: '/media/:path*',
        destination: process.env.INTERNAL_API_URL
          ? `${process.env.INTERNAL_API_URL}/media/:path*`
          : 'http://127.0.0.1:8001/media/:path*',
      },
    ];
  },
};

export default nextConfig;
