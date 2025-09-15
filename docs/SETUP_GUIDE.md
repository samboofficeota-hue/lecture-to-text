# Darwin セットアップガイド

## 概要

Darwin講義録生成システムの完全なセットアップ手順を説明します。

## 前提条件

### 1. 必要なアカウント
- **Google Cloud Platform** - プロジェクト作成済み
- **OpenAI** - APIキー取得済み
- **CloudFlare** - アカウント作成済み
- **Vercel** - アカウント作成済み
- **GitHub** - リポジトリ作成済み

### 2. 必要なツール
- Python 3.11+
- Node.js 18+
- Docker
- Vercel CLI
- Google Cloud SDK

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/darwin-lecture-to-text.git
cd darwin-lecture-to-text
```

### 2. 環境変数の設定

```bash
# 環境変数ファイルをコピー
cp env.example .env

# 環境変数を編集
nano .env
```

必要な環境変数：
- `GCP_PROJECT_ID`: Google Cloud プロジェクトID
- `OPENAI_API_KEY`: OpenAI APIキー
- `CLOUDFLARE_API_TOKEN`: CloudFlare APIトークン
- `CLOUDFLARE_ZONE_ID`: CloudFlare ゾーンID
- `VERCEL_ORG_ID`: Vercel 組織ID
- `VERCEL_PROJECT_ID`: Vercel プロジェクトID
- `VERCEL_TOKEN`: Vercel トークン

### 3. 依存関係のインストール

```bash
# Python依存関係
pip install -r requirements.txt

# Node.js依存関係
npm install
```

### 4. 外部環境の自動セットアップ

```bash
# 全サービスのセットアップを実行
python scripts/setup_environment.py
```

このスクリプトは以下を自動設定します：
- Google Cloud Storage
- Cloud SQL (PostgreSQL)
- Pub/Sub
- Cloud Tasks
- Cloud Logging
- CloudFlare
- Vercel

### 5. CloudFlareの詳細設定

```bash
# CloudFlareのDNS設定とセキュリティ設定
python scripts/setup_cloudflare.py
```

### 6. データベースの初期化

```bash
# データベーステーブルの作成
python scripts/init_database.py
```

### 7. テストの実行

```bash
# 単体テスト
pytest tests/

# 統合テスト
pytest tests/integration/
```

### 8. デプロイ

#### 開発環境

```bash
# Vercelにデプロイ
vercel --prod

# Cloud Runにデプロイ
gcloud run deploy darwin-api --source .
```

#### 本番環境

```bash
# GitHub Actionsで自動デプロイ
git push origin main
```

## 設定の確認

### 1. 外部環境接続の確認

```bash
# 接続テストを実行
python scripts/test_connections.py
```

### 2. 各サービスの状態確認

```bash
# GCS
gsutil ls gs://darwin-lecture-data

# Cloud SQL
gcloud sql instances list

# Pub/Sub
gcloud pubsub topics list

# Cloud Tasks
gcloud tasks queues list

# CloudFlare
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

## トラブルシューティング

### よくある問題

#### 1. 認証エラー
```bash
# Google Cloud認証
gcloud auth login
gcloud auth application-default login

# Vercel認証
vercel login
```

#### 2. 権限エラー
- Google Cloud IAMで必要な権限を確認
- CloudFlare APIトークンの権限を確認
- Vercelプロジェクトのアクセス権限を確認

#### 3. ネットワークエラー
- ファイアウォール設定を確認
- DNS設定を確認
- SSL証明書の状態を確認

### ログの確認

```bash
# アプリケーションログ
tail -f logs/darwin.log

# Cloud Logging
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Vercelログ
vercel logs
```

## メンテナンス

### 定期メンテナンス

1. **ログローテーション**
   ```bash
   # 古いログファイルを削除
   find logs/ -name "*.log.*" -mtime +30 -delete
   ```

2. **データベースバックアップ**
   ```bash
   # Cloud SQLバックアップ
   gcloud sql backups create --instance=darwin-db
   ```

3. **キャッシュクリア**
   ```bash
   # CloudFlareキャッシュクリア
   python scripts/clear_cache.py
   ```

### 監視設定

1. **アラート設定**
   - Cloud Monitoringでアラートを設定
   - エラー率、レスポンス時間、リソース使用率を監視

2. **ヘルスチェック**
   - `/health` エンドポイントでヘルスチェック
   - 定期的な接続テスト

## セキュリティ

### 1. 環境変数の管理
- 本番環境では環境変数を使用
- 機密情報はGitにコミットしない
- 定期的なキーローテーション

### 2. アクセス制御
- IAMロールの最小権限原則
- APIキーの適切な管理
- ネットワークアクセス制御

### 3. 監査
- アクセスログの監視
- 異常なアクセスの検出
- 定期的なセキュリティ監査

## サポート

問題が発生した場合：

1. ログを確認
2. 設定を再確認
3. ドキュメントを参照
4. 必要に応じてサポートに連絡

---

**注意**: 本番環境での使用前に、必ずテスト環境で動作確認を行ってください。
