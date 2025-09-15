# Darwin プロジェクト構造

## 概要

Darwin プロジェクトの整理されたディレクトリ構造とファイル配置について説明します。

## ディレクトリ構造

```
darwin/
├── 📁 adapters/                 # 外部サービス連携層
│   ├── file/                   # ファイル処理アダプター
│   ├── mygpt/                  # My GPTs連携アダプター
│   ├── openai/                 # OpenAI API連携アダプター
│   └── whisper/                # Whisper音声認識アダプター
├── 📁 config/                  # 設定管理層
│   ├── presets/               # 分野別設定プリセット
│   └── validators/            # 設定検証
├── 📁 content_generation/      # 資料作成機能（将来拡張）
│   ├── analysis/              # 分析機能
│   ├── discussion/            # ディスカッション資料
│   ├── summary/               # サマリー資料
│   └── textbook/              # テキストブック
├── 📁 core/                   # コア機能層
│   ├── interfaces/            # 抽象インターフェース
│   ├── models/                # データモデル
│   └── services/              # ビジネスロジック
├── 📁 data/                   # データストレージ
│   ├── corrections/           # 修正データ
│   ├── glossaries/            # 辞書データ
│   ├── learning_data/         # 学習データ
│   └── master_records/        # マスターレコード
├── 📁 docs/                   # ドキュメント
│   ├── ARCHITECTURE.md        # アーキテクチャ設計
│   ├── SYSTEM_ARCHITECTURE.md # システム構成
│   └── WHISPER_IMPROVEMENTS.md # Whisper改善
├── 📁 examples/               # 使用例・サンプル
├── 📁 glossaries/             # 辞書ファイル
│   ├── accounting_finance.csv # 会計・財務辞書
│   └── general.csv            # 一般辞書
├── 📁 learning/               # 学習・適応機能層
│   ├── correction/            # 修正学習
│   ├── domain/                # 分野検出
│   ├── glossary/              # 辞書管理
│   └── rag/                   # RAG管理
├── 📁 legacy/                 # レガシーコード
│   └── lecture_pipeline.py    # 旧パイプライン
├── 📁 master_management/      # マスターテキスト管理（将来拡張）
│   ├── quality/               # 品質管理
│   ├── record_manager/        # 記録管理
│   └── storage/               # ストレージ管理
├── 📁 scripts/                # デプロイ・運用スクリプト
│   ├── cloud_run_api.py       # Cloud Run API
│   └── deploy-cloud-run.sh    # デプロイスクリプト
├── 📁 src/                    # Next.jsフロントエンド
│   └── app/                   # App Router
├── 📁 tests/                  # テストフレームワーク
│   ├── fixtures/              # テストデータ
│   ├── integration/           # 統合テスト
│   └── unit/                  # 単体テスト
├── 📁 ui/                     # UI層（将来拡張）
│   ├── cli/                   # コマンドラインUI
│   ├── interactive/           # 対話型UI
│   └── web/                   # Web UI
├── 📁 utils/                  # ユーティリティ層
│   ├── file_utils/            # ファイル操作
│   ├── logging/               # ログ管理
│   └── text_utils/            # テキスト処理
├── 📁 venv/                   # Python仮想環境
├── 📄 main.py                 # メインエントリーポイント
├── 📄 requirements.txt        # Python依存関係
├── 📄 package.json            # Node.js依存関係
├── 📄 Dockerfile              # Docker設定
├── 📄 vercel.json             # Vercel設定
├── 📄 .gitignore              # Git除外設定
├── 📄 env.example             # 環境変数例
└── 📄 README.md               # プロジェクト説明
```

## ファイル分類

### 🗑️ 削除されたファイル
- `config.py` → `config/settings.py` に統合
- `text_enhancer.py` → `adapters/openai/` に統合
- `test_system.py` → `tests/` に移動予定
- `test_audio.wav` → テストデータとして不要

### 📁 新規作成されたディレクトリ
- `docs/` - ドキュメント集約
- `scripts/` - デプロイ・運用スクリプト
- `examples/` - 使用例・サンプル
- `legacy/` - レガシーコード
- `env.example` - 環境変数設定例

### 🔄 移動されたファイル
- `ARCHITECTURE.md` → `docs/`
- `SYSTEM_ARCHITECTURE.md` → `docs/`
- `WHISPER_IMPROVEMENTS.md` → `docs/`
- `deploy-cloud-run.sh` → `scripts/`
- `cloud_run_api.py` → `scripts/`
- `lecture_pipeline.py` → `legacy/`
- `glossary.csv` → `glossaries/general.csv`

## ディレクトリの役割

### コア機能層 (`core/`)
- **interfaces/**: 抽象インターフェース定義
- **models/**: データモデル定義
- **services/**: ビジネスロジック実装

### 外部サービス連携層 (`adapters/`)
- **whisper/**: 音声認識エンジン連携
- **openai/**: OpenAI API連携
- **file/**: ファイル処理連携
- **mygpt/**: My GPTs連携

### 学習・適応機能層 (`learning/`)
- **glossary/**: 辞書管理・自動生成
- **correction/**: 修正学習
- **domain/**: 分野検出
- **rag/**: RAGシステム管理

### 設定管理層 (`config/`)
- **settings.py**: アプリケーション設定
- **presets/**: 分野別設定プリセット

### データ層 (`data/`, `glossaries/`)
- **data/**: アプリケーション実行時データ
- **glossaries/**: 辞書ファイル（CSV）

### ユーティリティ層 (`utils/`)
- **logging/**: ログ管理
- **file_utils/**: ファイル操作
- **text_utils/**: テキスト処理

## 命名規則

### ディレクトリ
- **小文字 + アンダースコア**: `file_utils/`
- **単数形**: `adapter/` (複数形は避ける)

### ファイル
- **Python**: `snake_case.py`
- **TypeScript**: `camelCase.tsx`
- **設定ファイル**: `kebab-case.json`

### クラス・関数
- **Python**: `PascalCase` (クラス), `snake_case` (関数)
- **TypeScript**: `PascalCase` (クラス), `camelCase` (関数)

## 依存関係

### Python依存関係
- **requirements.txt**: 本番環境用
- **venv/**: 開発環境用仮想環境

### Node.js依存関係
- **package.json**: フロントエンド依存関係
- **node_modules/**: 依存関係パッケージ

## 環境設定

### 環境変数
- **env.example**: 設定例ファイル
- **.env**: 実際の設定（Git除外）

### 設定ファイル
- **config/settings.py**: アプリケーション設定
- **config/presets/**: 分野別設定

## テスト

### テスト構造
- **tests/unit/**: 単体テスト
- **tests/integration/**: 統合テスト
- **tests/fixtures/**: テストデータ

## デプロイ

### スクリプト
- **scripts/deploy-cloud-run.sh**: Cloud Runデプロイ
- **scripts/cloud_run_api.py**: Cloud Run API

### 設定ファイル
- **Dockerfile**: Docker設定
- **vercel.json**: Vercel設定

## 今後の拡張

### 将来機能
- **content_generation/**: 資料作成機能
- **master_management/**: マスターテキスト管理
- **ui/**: 各種UI実装

### レガシーコード
- **legacy/**: 旧コードの保存・参照用
