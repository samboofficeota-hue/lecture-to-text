# Lecture-to-Text システムアーキテクチャ

## 概要
多分野の講義に対応できる柔軟で拡張可能な音声認識・文字起こしシステム

## アーキテクチャの基本原則

### 1. 関心の分離 (Separation of Concerns)
- 音声処理、文字起こし、テキスト処理、出力生成を分離
- 各モジュールが独立してテスト・修正可能

### 2. 依存性の逆転 (Dependency Inversion)
- 抽象インターフェースに依存
- 具体的な実装は実行時に注入

### 3. 開閉原則 (Open/Closed Principle)
- 新機能追加時は既存コードを変更せず拡張
- プラグイン方式で機能追加

### 4. 単一責任原則 (Single Responsibility)
- 各クラス・モジュールは一つの責任のみ
- 変更理由が一つに限定される

## システム構成

```
lecture-to-text/
├── core/                           # コア機能層
│   ├── __init__.py
│   ├── interfaces/                 # 抽象インターフェース
│   │   ├── __init__.py
│   │   ├── audio_processor.py
│   │   ├── transcriber.py
│   │   ├── text_processor.py
│   │   └── output_generator.py
│   ├── services/                   # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── transcription_service.py
│   │   ├── text_processing_service.py
│   │   └── output_service.py
│   └── models/                     # データモデル
│       ├── __init__.py
│       ├── audio_data.py
│       ├── transcription_data.py
│       └── processing_result.py
├── adapters/                       # 外部サービス連携層
│   ├── __init__.py
│   ├── whisper/                    # Whisper関連
│   │   ├── __init__.py
│   │   ├── whisper_adapter.py
│   │   └── whisper_config.py
│   ├── openai/                     # OpenAI関連
│   │   ├── __init__.py
│   │   ├── openai_adapter.py
│   │   └── openai_config.py
│   └── file/                       # ファイル操作
│       ├── __init__.py
│       ├── file_adapter.py
│       └── format_converters.py
├── learning/                       # 学習・適応機能層
│   ├── __init__.py
│   ├── glossary/                   # 辞書管理
│   │   ├── __init__.py
│   │   ├── glossary_manager.py
│   │   ├── auto_glossary_generator.py
│   │   └── domain_glossary_loader.py
│   ├── correction/                 # 修正学習
│   │   ├── __init__.py
│   │   ├── correction_learner.py
│   │   ├── pattern_analyzer.py
│   │   └── correction_suggester.py
│   └── domain/                     # 分野検出
│       ├── __init__.py
│       ├── domain_detector.py
│       ├── keyword_extractor.py
│       └── domain_classifier.py
├── ui/                            # ユーザーインターフェース層
│   ├── __init__.py
│   ├── cli/                        # コマンドライン
│   │   ├── __init__.py
│   │   ├── cli_interface.py
│   │   └── command_handlers.py
│   ├── web/                        # Web UI
│   │   ├── __init__.py
│   │   ├── web_interface.py
│   │   ├── templates/
│   │   └── static/
│   └── interactive/                # インタラクティブ修正
│       ├── __init__.py
│       ├── correction_interface.py
│       └── real_time_editor.py
├── config/                        # 設定管理層
│   ├── __init__.py
│   ├── settings.py                 # 設定管理
│   ├── presets/                    # プリセット
│   │   ├── __init__.py
│   │   ├── academic_preset.py
│   │   ├── business_preset.py
│   │   └── technical_preset.py
│   └── validators/                 # 設定検証
│       ├── __init__.py
│       └── config_validator.py
├── data/                          # データ管理層
│   ├── glossaries/                 # 辞書データ
│   │   ├── base/                   # 基本辞書
│   │   ├── domain/                 # 分野別辞書
│   │   └── learned/                # 学習済み辞書
│   ├── corrections/                # 修正データ
│   │   ├── patterns/               # 修正パターン
│   │   └── history/                # 修正履歴
│   └── learning_data/              # 学習データ
│       ├── training/               # 訓練データ
│       └── validation/             # 検証データ
├── utils/                         # ユーティリティ層
│   ├── __init__.py
│   ├── logging/                    # ログ管理
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── file_utils/                 # ファイル操作
│   │   ├── __init__.py
│   │   └── file_utils.py
│   └── text_utils/                 # テキスト処理
│       ├── __init__.py
│       └── text_utils.py
├── tests/                         # テスト層
│   ├── __init__.py
│   ├── unit/                       # 単体テスト
│   ├── integration/                # 統合テスト
│   └── fixtures/                   # テストデータ
├── docs/                          # ドキュメント
│   ├── api/                        # API仕様
│   ├── user_guide/                 # ユーザーガイド
│   └── developer_guide/            # 開発者ガイド
├── main.py                        # エントリーポイント
├── requirements.txt               # 依存関係
├── setup.py                       # セットアップ
└── README.md                      # プロジェクト概要
```

## データフロー

```
音声ファイル → 音声処理 → 文字起こし → テキスト処理 → 学習・適応 → 出力生成
     ↓              ↓           ↓            ↓           ↓          ↓
   AudioData → Transcription → ProcessedText → LearnedData → Output
```

## 主要コンポーネント

### 1. コア機能層 (core/)
- **interfaces/**: 抽象インターフェース定義
- **services/**: ビジネスロジック実装
- **models/**: データモデル定義

### 2. アダプター層 (adapters/)
- **whisper/**: Whisper音声認識エンジン連携
- **openai/**: OpenAI API連携
- **file/**: ファイル入出力処理

### 3. 学習・適応機能層 (learning/)
- **glossary/**: 辞書管理・自動生成
- **correction/**: 修正パターン学習
- **domain/**: 分野検出・分類

### 4. UI層 (ui/)
- **cli/**: コマンドラインインターフェース
- **web/**: WebベースUI
- **interactive/**: インタラクティブ修正

### 5. 設定管理層 (config/)
- **settings.py**: 設定管理
- **presets/**: 分野別プリセット
- **validators/**: 設定検証

## 拡張ポイント

1. **新しい音声認識エンジン**: adapters/に新しいアダプターを追加
2. **新しい出力形式**: core/services/output_service.pyを拡張
3. **新しい学習アルゴリズム**: learning/に新しいモジュールを追加
4. **新しいUI**: ui/に新しいインターフェースを追加

## 設定管理

- 環境変数による設定
- 設定ファイル（YAML/JSON）
- コマンドライン引数
- プリセットによる一括設定

## ログ・監視

- 構造化ログ（JSON形式）
- ログレベル管理
- パフォーマンス監視
- エラー追跡

## テスト戦略

- 単体テスト（各モジュール）
- 統合テスト（モジュール間連携）
- エンドツーエンドテスト（全体フロー）
- パフォーマンステスト
