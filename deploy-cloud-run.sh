#!/bin/bash

# Cloud Run デプロイスクリプト
# 使用方法: ./deploy-cloud-run.sh

# 設定
PROJECT_ID="lecture-to-text-472009"
SERVICE_NAME="lecture-to-text-api"
REGION="asia-northeast1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Cloud Run デプロイを開始します..."

# 1. Google Cloud SDKがインストールされているか確認
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDKがインストールされていません"
    echo "https://cloud.google.com/sdk/docs/install からインストールしてください"
    exit 1
fi

# 2. プロジェクトIDを設定
echo "📝 プロジェクトIDを設定中..."
gcloud config set project $PROJECT_ID

# 3. Dockerイメージをビルド
echo "🔨 Dockerイメージをビルド中..."
gcloud builds submit --tag $IMAGE_NAME .

# 4. Cloud Runにデプロイ
echo "☁️ Cloud Runにデプロイ中..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "OPENAI_API_KEY=\$OPENAI_API_KEY" \
    --set-env-vars "MAX_CONTENT_LENGTH=100MB" \
    --set-env-vars "UPLOAD_MAX_SIZE=100MB" \
    --set-env-vars "FLASK_MAX_CONTENT_LENGTH=100MB" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

echo "✅ デプロイ完了！"
echo "🌐 サービスURL: https://$SERVICE_NAME-$REGION-$PROJECT_ID.a.run.app"
