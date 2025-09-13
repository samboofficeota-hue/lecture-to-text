# Cloudflare設定ガイド

## 1. ドメインの準備

### 推奨ドメイン名
- `lecture-to-text.com`
- `lecture-to-text.net`
- `lecture-to-text.org`
- `lecture-to-text.app`

## 2. Cloudflare設定手順

### Step 1: ドメインの追加
1. [Cloudflare Dashboard](https://dash.cloudflare.com) にログイン
2. "Add a Site" をクリック
3. ドメイン名を入力
4. プランを選択（Free プランで十分）

### Step 2: DNS設定
```
Type    Name    Content                                    TTL
A       @       Vercel IP (76.76.19.61)                   Auto
CNAME   www     cname.vercel-dns.com                       Auto
```

### Step 3: SSL/TLS設定
- **SSL/TLS encryption mode**: Full (strict)
- **Always Use HTTPS**: ON
- **HTTP Strict Transport Security (HSTS)**: ON

### Step 4: パフォーマンス設定
- **Auto Minify**: CSS, JavaScript, HTML を有効化
- **Brotli Compression**: ON
- **Rocket Loader**: ON
- **Mirage**: ON

### Step 5: セキュリティ設定
- **Security Level**: Medium
- **Bot Fight Mode**: ON
- **Challenge Passage**: 1時間
- **Browser Integrity Check**: ON

## 3. Vercelとの連携

### カスタムドメインの追加
```bash
# Vercelにカスタムドメインを追加
vercel domains add lecture-to-text.com
vercel domains add www.lecture-to-text.com
```

### 環境変数の設定
```bash
# Vercelに環境変数を設定
vercel env add CLOUD_RUN_API_URL production
# 値: https://lecture-to-text-api-1088729528504.asia-northeast1.run.app
```

## 4. 設定確認

### DNS設定の確認
```bash
# DNS設定を確認
nslookup lecture-to-text.com
dig lecture-to-text.com
```

### SSL証明書の確認
```bash
# SSL証明書を確認
openssl s_client -connect lecture-to-text.com:443 -servername lecture-to-text.com
```

## 5. パフォーマンステスト

### PageSpeed Insights
- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- ドメイン: `https://lecture-to-text.com`

### GTmetrix
- [GTmetrix](https://gtmetrix.com/)
- ドメイン: `https://lecture-to-text.com`

## 6. 監視設定

### Cloudflare Analytics
- トラフィック分析
- セキュリティ分析
- パフォーマンス分析

### Uptime Monitoring
- Cloudflare Uptime Monitoring を有効化
- アラート設定（メール通知）
