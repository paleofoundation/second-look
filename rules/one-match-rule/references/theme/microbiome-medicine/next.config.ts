import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  trailingSlash: false,
  // Proxy handles host + trailing-slash + `/?s=` in a single hop.
  skipTrailingSlashRedirect: true,
  async redirects() {
    return [
      { source: "/about", destination: "/about-us", permanent: true },
      { source: "/author/karen", destination: "/author/kmfp84gmail-com", permanent: true },
      { source: "/author/karen-pendergrass", destination: "/author/kmfp84gmail-com", permanent: true },
      { source: "/author/:slug/page/:n", destination: "/author/:slug?page=:n", permanent: true },
      { source: "/membership-2", destination: "/membership", permanent: true },
      { source: "/microbiome-signatures-home-new", destination: "/", permanent: true },
      { source: "/category/conditions", destination: "/conditions", permanent: true },
      { source: "/category/microbes", destination: "/microbes", permanent: true },
      { source: "/category/interventions", destination: "/interventions", permanent: true },
      { source: "/category/definition", destination: "/definition", permanent: true },
      { source: "/category/definitions", destination: "/definition", permanent: true },
      { source: "/category/metals", destination: "/metals", permanent: true },
      { source: "/category/supplement", destination: "/supplement", permanent: true },
      { source: "/category/supplements", destination: "/supplement", permanent: true },
      { source: "/category/guide", destination: "/guide", permanent: true },
      { source: "/category/guides", destination: "/guide", permanent: true },
      { source: "/category/research-feeds", destination: "/research-feeds", permanent: true },
      { source: "/category/research", destination: "/research-feeds", permanent: true },
      { source: "/category/:path*", destination: "/", permanent: true },
      { source: "/tag/:path*", destination: "/", permanent: true },
      { source: "/page/:path*", destination: "/blog", permanent: true },
    ];
  },
};

export default nextConfig;
