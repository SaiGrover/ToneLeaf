/** @type {import('next').NextConfig} */
const staticExport = process.env.TONELEAF_STATIC_EXPORT === "1";

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  ...(staticExport ? { output: "export" } : {}),
};

export default nextConfig;
