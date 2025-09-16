import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 静的ファイルの最適化
  images: {
    unoptimized: true
  }
};

export default nextConfig;
