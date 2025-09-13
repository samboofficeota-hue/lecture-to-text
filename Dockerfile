# Cloud Run用Dockerfile
FROM python:3.11-slim

# システムパッケージの更新とFFmpegのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー（不要なファイルを除外）
COPY cloud_run_api.py .
COPY text_enhancer.py .
COPY config.py .

# ポート8080を公開（Cloud Runのデフォルト）
EXPOSE 8080

# 環境変数の設定
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ヘルスチェック用のエンドポイント
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# アプリケーションの起動
CMD ["python", "cloud_run_api.py"]
