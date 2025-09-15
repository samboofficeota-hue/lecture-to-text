# Darwin Lecture Assistant ドキュメント

## 概要

Darwin Lecture Assistantの技術ドキュメント集です。プロジェクトの設計、実装、運用に関する詳細な情報を提供します。

## ドキュメント一覧

### アーキテクチャ設計

- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: クリーンアーキテクチャに基づくシステム設計
- **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)**: クラウドシステム全体のアーキテクチャ

### 実装・統合

- **[MYGPT_INTEGRATION_RESULTS.md](./MYGPT_INTEGRATION_RESULTS.md)**: MyGPTs統合の成果レポート
- **[MYGPT_OPTIMIZATION_TIPS.md](./MYGPT_OPTIMIZATION_TIPS.md)**: MyGPTsを賢くするためのコツ

### セットアップ・運用

- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)**: 環境構築とセットアップガイド
- **[WHISPER_IMPROVEMENTS.md](./WHISPER_IMPROVEMENTS.md)**: Whisperの改善点と最適化

## 主要な成果

### ✅ 完了した機能

1. **クリーンアーキテクチャの実装**
   - レガシーコードの分割・再構築
   - 依存関係の逆転
   - テスタビリティの向上

2. **MyGPTs統合**
   - Darwin Lecture Assistantの作成
   - 専門用語の統一機能
   - 概念の統一機能

3. **外部サービス連携**
   - Google Cloud Run
   - Google Cloud Storage
   - Cloud SQL
   - CloudFlare
   - Vercel

4. **CI/CD環境**
   - GitHub Actions
   - 自動デプロイ
   - 環境管理

### 🚧 進行中の機能

1. **用語集の拡充**
   - 経済学用語集の追加
   - 分野別用語集の充実

2. **プロンプトの最適化**
   - より良い結果を得るための調整
   - 分野別プロンプトの開発

### 📋 今後の予定

1. **実際の講義データでのテスト**
   - より長い講義テキストでのテスト
   - 実際の使用ケースでの検証

2. **教材生成機能の実装**
   - サマリー文書の自動生成
   - ディスカッション用テーマシートの作成
   - テキストブック形式での教材生成

## 技術スタック

### フロントエンド
- Next.js (React)
- TypeScript
- Tailwind CSS

### バックエンド
- Python
- Flask
- OpenAI Whisper
- ChatGPT API
- MyGPTs「Darwin Lecture Assistant」

### クラウド
- Vercel (フロントエンド)
- Google Cloud Run (バックエンド)
- Google Cloud Storage (ファイルストレージ)
- Cloud SQL (データベース)
- CloudFlare (CDN・セキュリティ)

### アーキテクチャ
- クリーンアーキテクチャ
- マイクロサービス
- 依存関係の逆転
- テスタビリティ

## 使用方法

### 基本的な使用方法

1. **音声ファイルのアップロード**
   - MP3、WAV、M4A等の音声ファイルをアップロード

2. **講義の処理**
   - 音声文字起こし（Whisper）
   - 専門用語の統一（MyGPTs）
   - 概念の統一（MyGPTs）

3. **結果の確認**
   - 改善されたテキストの確認
   - 用語の統一表の確認
   - 改善提案の確認

### 高度な使用方法

1. **用語集の管理**
   - 分野別用語集の追加
   - 用語の更新・削除

2. **プロンプトのカスタマイズ**
   - 分野別プロンプトの設定
   - 出力形式のカスタマイズ

3. **品質の最適化**
   - フィードバックに基づく改善
   - 継続的な品質向上

## 貢献

プロジェクトへの貢献を歓迎します。以下の方法で貢献できます：

1. **バグレポート**: 問題を発見した場合は、Issueを作成してください
2. **機能要望**: 新しい機能の要望がある場合は、Issueを作成してください
3. **プルリクエスト**: コードの改善や新機能の実装をプルリクエストで送信してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 連絡先

プロジェクトに関する質問や提案がある場合は、Issueを作成してください。
