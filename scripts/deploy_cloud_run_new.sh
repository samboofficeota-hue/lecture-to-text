#!/bin/bash
"""
新しいアーキテクチャ用Cloud Runデプロイスクリプト
"""

set -e

# 設定
PROJECT_ID="lecture-to-text-472009"
REGION="asia-northeast1"
SERVICE_NAME="darwin-lecture-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 新しいアーキテクチャ用Cloud Runサービスをデプロイ中..."

# プロジェクトを設定
gcloud config set project ${PROJECT_ID}

# Dockerイメージをビルド
echo "📦 Dockerイメージをビルド中..."
gcloud builds submit --tag ${IMAGE_NAME} --file Dockerfile.new .

# Cloud Runサービスをデプロイ
echo "🚀 Cloud Runサービスをデプロイ中..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 100 \
  --set-env-vars "PORT=8080,PYTHONUNBUFFERED=1,PYTHONPATH=/app,GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION},LOG_LEVEL=INFO,MAX_CONTENT_LENGTH=104857600"

echo "✅ デプロイ完了！"
echo "🌐 サービスURL: https://${SERVICE_NAME}-${PROJECT_ID}.${REGION}.run.app"
