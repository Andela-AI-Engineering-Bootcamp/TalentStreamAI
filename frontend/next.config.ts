import type { NextConfig } from "next";

// Static export is for `next build` / the production Dockerfile only. Keep it off for
// `next dev` (including Docker Compose) so the dev server behaves normally.
const useStaticExport = process.env.NEXT_STATIC_EXPORT === "1";

const nextConfig: NextConfig = {
  ...(useStaticExport ? { output: "export" as const } : {}),
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
