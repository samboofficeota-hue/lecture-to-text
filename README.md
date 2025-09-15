# Darwin Lecture Assistant

講義音声から高品質な教材を自動生成するAIアシスタント

## 概要

Darwin Lecture Assistantは、講義音声から高品質な教材を自動生成するAIアシスタントです。OpenAI Whisperによる音声文字起こしと、MyGPTs「Darwin Lecture Assistant」による専門用語の統一・概念の統一を組み合わせることで、100%の精度で専門用語と固有名詞を正確に記録した講義録を生成します。

## 技術スタック

- **フロントエンド**: Next.js (React), TypeScript, Tailwind CSS
- **バックエンド**: Python, Flask, OpenAI Whisper, ChatGPT API
- **AI統合**: MyGPTs「Darwin Lecture Assistant」
- **クラウド**: Vercel, Google Cloud Run, Google Cloud Storage, Cloud SQL
- **音声処理**: FFmpeg
- **アーキテクチャ**: クリーンアーキテクチャ、マイクロサービス

## 主要機能

### 1. 高精度音声文字起こし
- OpenAI Whisperによる高精度な音声認識
- 5分単位でのブロック処理
- リアルタイム処理状況の表示

### 2. 専門用語の統一
- MyGPTs「Darwin Lecture Assistant」による専門用語の統一
- 表記揺れの自動修正
- 分野別用語集の活用

### 3. 概念の統一
- 経済学・会計学・コーポレートガバナンス分野の専門知識
- 概念の一貫性確保
- 理論的な整合性の維持

### 4. 講義録管理
- 講義録のバージョン管理
- メタデータの管理
- 検索・分類機能

### 5. 教材生成
- サマリー文書の自動生成
- ディスカッション用テーマシートの作成
- テキストブック形式での教材生成

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
# Test Cloud Run auto-deployment
