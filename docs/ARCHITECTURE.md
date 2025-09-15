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
│   │   ├── output_generator.py
│   │   ├── rag_interface.py
│   │   └── pdf_processor.py
│   ├── services/                   # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── transcription_service.py
│   │   ├── text_processing_service.py
│   │   ├── output_service.py
│   │   ├── rag_service.py
│   │   └── pdf_analysis_service.py
│   └── models/                     # データモデル
│       ├── __init__.py
│       ├── audio_data.py
│       ├── transcription_data.py
│       ├── processing_result.py
│       ├── lecture_record.py
│       └── master_text.py
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
│   ├── mygpt/                      # My GPTs連携
│   │   ├── __init__.py
│   │   ├── mygpt_rag_adapter.py
│   │   └── mygpt_config.py
│   └── file/                       # ファイル操作
│       ├── __init__.py
│       ├── file_adapter.py
│       ├── format_converters.py
│       └── pdf_reader.py
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
│   ├── domain/                     # 分野検出
│   │   ├── __init__.py
│   │   ├── domain_detector.py
│   │   ├── keyword_extractor.py
│   │   └── domain_classifier.py
│   └── rag/                        # RAG機能
│       ├── __init__.py
│       ├── rag_manager.py
│       ├── knowledge_base.py
│       └── mygpt_integration.py
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
├── content_generation/             # 資料作成機能層
│   ├── __init__.py
│   ├── summary/                    # サマリー資料作成
│   │   ├── __init__.py
│   │   ├── summary_generator.py
│   │   ├── chart_generator.py
│   │   └── layout_optimizer.py
│   ├── discussion/                 # ディスカッション用資料
│   │   ├── __init__.py
│   │   ├── theme_generator.py
│   │   ├── question_generator.py
│   │   └── discussion_guide.py
│   ├── textbook/                   # テキストブック作成
│   │   ├── __init__.py
│   │   ├── chapter_organizer.py
│   │   ├── content_structure.py
│   │   └── textbook_formatter.py
│   └── analysis/                   # 講義内容分析
│       ├── __init__.py
│       ├── keyword_analyzer.py
│       ├── importance_scorer.py
│       └── curriculum_optimizer.py
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
│   ├── learning_data/              # 学習データ
│   │   ├── training/               # 訓練データ
│   │   └── validation/             # 検証データ
│   └── master_records/             # 講義録マスターデータ
│       ├── lectures/               # 講義データ
│       │   ├── audio/              # 元音声データ
│       │   ├── materials/          # 講義資料
│       │   ├── transcripts/        # 文字起こしデータ
│       │   └── metadata/           # メタデータ
│       └── versions/               # バージョン管理
│           ├── raw/                # 初期テキスト
│           ├── processed/          # 処理済みテキスト
│           └── final/              # 最終テキスト
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
├── master_management/              # 講義録マスターテキスト管理層
│   ├── __init__.py
│   ├── record_manager/             # 記録管理
│   │   ├── __init__.py
│   │   ├── lecture_record_manager.py
│   │   ├── version_controller.py
│   │   └── metadata_manager.py
│   ├── storage/                    # ストレージ管理
│   │   ├── __init__.py
│   │   ├── file_storage.py
│   │   ├── database_manager.py
│   │   └── backup_manager.py
│   └── quality/                    # 品質管理
│       ├── __init__.py
│       ├── quality_checker.py
│       ├── validation_service.py
│       └── feedback_processor.py
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

### 基本フロー
```
音声ファイル → 音声処理 → 文字起こし → テキスト処理 → 学習・適応 → 出力生成
     ↓              ↓           ↓            ↓           ↓          ↓
   AudioData → Transcription → ProcessedText → LearnedData → Output
```

### 拡張フロー（RAG連携）
```
PDF資料 → PDF分析 → 辞書準備 → 音声処理 → 文字起こし → RAG連携 → テキスト処理 → 学習・適応 → 出力生成
   ↓         ↓         ↓         ↓           ↓         ↓         ↓           ↓          ↓
PDFData → Analysis → Glossary → AudioData → Transcription → RAG → ProcessedText → LearnedData → Output
```

### マスターテキスト管理フロー
```
講義録作成 → バージョン管理 → 品質チェック → マスターテキスト保存 → 資料生成
     ↓            ↓            ↓              ↓                ↓
  Creation → VersionControl → QualityCheck → MasterStorage → ContentGeneration
```

## 主要コンポーネント

### 1. コア機能層 (core/)
- **interfaces/**: 抽象インターフェース定義
- **services/**: ビジネスロジック実装
- **models/**: データモデル定義

### 2. アダプター層 (adapters/)
- **whisper/**: Whisper音声認識エンジン連携
- **openai/**: OpenAI API連携
- **mygpt/**: My GPTs RAG連携
- **file/**: ファイル入出力処理

### 3. 学習・適応機能層 (learning/)
- **glossary/**: 辞書管理・自動生成
- **correction/**: 修正パターン学習
- **domain/**: 分野検出・分類
- **rag/**: RAG機能・知識ベース管理

### 4. UI層 (ui/)
- **cli/**: コマンドラインインターフェース
- **web/**: WebベースUI
- **interactive/**: インタラクティブ修正

### 5. 資料作成機能層 (content_generation/)
- **summary/**: サマリー資料作成
- **discussion/**: ディスカッション用資料
- **textbook/**: テキストブック作成
- **analysis/**: 講義内容分析

### 6. 講義録マスターテキスト管理層 (master_management/)
- **record_manager/**: 講義記録管理
- **storage/**: ストレージ管理
- **quality/**: 品質管理

### 7. 設定管理層 (config/)
- **settings.py**: 設定管理
- **presets/**: 分野別プリセット
- **validators/**: 設定検証

## 拡張ポイント

### 基本機能拡張
1. **新しい音声認識エンジン**: adapters/に新しいアダプターを追加
2. **新しい出力形式**: core/services/output_service.pyを拡張
3. **新しい学習アルゴリズム**: learning/に新しいモジュールを追加
4. **新しいUI**: ui/に新しいインターフェースを追加

### 将来機能拡張

#### 1. 講義録マスターテキスト管理システム
- **データ管理**: 元音声データ、講義資料、初期テキスト、最終テキストの完全な記録
- **バージョン管理**: 修正履歴の追跡とロールバック機能
- **メタデータ管理**: 講義情報、分野、日付、講師情報の管理

#### 2. 資料作成機能群
- **サマリー資料作成**: A4サイズ1枚の要約資料（チャート図含む）
- **ディスカッション用テーマシート**: グループディスカッション用のテーマ・質問生成
- **テキストブック作成**: チャプター分けされた読み物形式の教材生成

#### 3. 高度な分析機能
- **講義内容分析**: キーワード分析、重要度スコアリング
- **学習効果予測**: 講義内容と学習成果の相関分析
- **カリキュラム最適化**: 複数講義の関連性分析と最適な順序提案

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
