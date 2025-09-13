# lecture-to-text
講義動画から教材を自動生成するWebアプリケーション

## 概要
ZOOM録画やYouTube動画から音声を抽出し、OpenAI Whisperで文字起こしを行い、ChatGPTでテキストを強化して講義録・教材を自動生成するWebアプリケーションです。

## 技術スタック
- **フロントエンド**: Next.js (React), TypeScript, Tailwind CSS
- **バックエンド**: Python, Flask, OpenAI Whisper, ChatGPT API
- **クラウド**: Vercel, Google Cloud Run, Vercel Blob Storage
- **動画処理**: FFmpeg, yt-dlp

## 機能
1. 動画URL入力（ZOOM録画・YouTube対応）
2. 音声抽出・文字起こし（Whisper）
3. テキスト強化（ChatGPT）
4. 講義録・サマリー・教材生成
5. 講義記録管理

## セットアップ

### ローカル開発
```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev
```

### 環境変数
```bash
OPENAI_API_KEY=your_openai_api_key
```

## デプロイ
- **フロントエンド**: Vercel
- **バックエンド**: Google Cloud Run
- **ストレージ**: Vercel Blob Storage
