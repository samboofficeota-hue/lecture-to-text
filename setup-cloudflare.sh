#!/bin/bash

# Cloudflare設定スクリプト
# 使用方法: ./setup-cloudflare.sh

echo "🌐 Cloudflare設定を開始します..."

# 1. Wrangler CLIのインストール確認
if ! command -v wrangler &> /dev/null; then
    echo "📦 Wrangler CLIをインストール中..."
    npm install -g wrangler
fi

# 2. Cloudflare認証
echo "🔐 Cloudflareにログインしてください..."
wrangler login

# 3. ドメインの設定
echo "📝 ドメインを設定中..."
read -p "使用するドメイン名を入力してください (例: lecture-to-text.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ ドメイン名が入力されていません"
    exit 1
fi

# 4. Vercelにカスタムドメインを追加
echo "🔗 Vercelにカスタムドメインを追加中..."
vercel domains add $DOMAIN
vercel domains add www.$DOMAIN

# 5. 環境変数の設定
echo "⚙️ 環境変数を設定中..."
vercel env add CLOUD_RUN_API_URL production
echo "値: https://lecture-to-text-api-1088729528504.asia-northeast1.run.app"

# 6. DNS設定の確認
echo "🔍 DNS設定を確認中..."
echo "以下のDNS設定をCloudflareで行ってください:"
echo "Type: A, Name: @, Content: 76.76.19.61"
echo "Type: CNAME, Name: www, Content: cname.vercel-dns.com"

# 7. SSL設定の確認
echo "🔒 SSL設定を確認中..."
echo "Cloudflareで以下の設定を行ってください:"
echo "- SSL/TLS encryption mode: Full (strict)"
echo "- Always Use HTTPS: ON"
echo "- HTTP Strict Transport Security (HSTS): ON"

echo "✅ Cloudflare設定が完了しました！"
echo "🌐 ドメイン: https://$DOMAIN"
echo "📊 Cloudflare Dashboard: https://dash.cloudflare.com"
