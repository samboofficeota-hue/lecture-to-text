# Cloud Run用Dockerfile
FROM python:3.11-slim

# システムパッケージの更新とFFmpegのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8080を公開（Cloud Runのデフォルト）
EXPOSE 8080

# 環境変数の設定
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# アプリケーションの起動
CMD ["python", "cloud_run_api.py"]
