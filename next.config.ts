import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // APIルートを無効化（直接Cloud Runを使用）
  experimental: {
    serverComponentsExternalPackages: []
  },
  // 静的ファイルの最適化
  images: {
    unoptimized: true
  }
};

export default nextConfig;
