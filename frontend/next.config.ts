import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        // Use the container_name (unique on the Docker host) instead of the
        // generic "backend" service alias — multiple unrelated apps on the
        // shared "proxy" network also publish a "backend" alias, causing DNS
        // round-robin and intermittent 404s.
        destination: "http://scraper-api:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
