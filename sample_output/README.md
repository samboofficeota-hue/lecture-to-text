# 文字起こしと文章ブラッシュアップ サンプル出力

このディレクトリには、Whisperで書き起こした講義音声を、文章のブラッシュアップ機能で改善したサンプルファイルが含まれています。

## ファイル構成

### 入力ファイル
- `transcript.raw.txt` - Whisperで書き起こした生のテキスト（機械学習入門講義）

### 中間処理ファイル
- `transcript.norm.txt` - 用語辞書を適用した正規化テキスト
- `unknown_terms.csv` - 未知語候補のリスト（頻度付き）

### 出力ファイル

#### 従来の処理
- `textbook_draft.md` - 基本的なMarkdownドラフト（段落メモ形式）

#### ChatGPT APIを使用した高度な処理
- `transcript.enhanced.txt` - ChatGPT APIで改善されたテキスト
- `full_transcript.md` - 完成度の高い講義録（章立て、学習目標、用語集、確認問題付き）
- `technical_terms.txt` - 抽出された専門用語リスト（54個）

## 改善のポイント

### 1. 用語辞書による正規化
- 「ディープラーニング」→「深層学習」への統一
- 専門用語の表記統一

### 2. ChatGPT APIによる文章改善
- 話し言葉から書き言葉への変換
- 文章の流れの自然化
- 専門用語の適切な使用
- 段落構成の整理

### 3. フル講義録の生成
- 学習目標の明確化
- 章立てによる構造化
- 重要用語集の作成
- 確認問題の生成
- 参考資料の提案

## 処理フロー

1. **音声抽出** → Whisperで文字起こし
2. **用語辞書適用** → 専門用語の表記統一
3. **未知語抽出** → 辞書にない用語の候補収集
4. **テキスト改善** → ChatGPT APIによる文章のブラッシュアップ
5. **講義録生成** → 完成度の高い講義録の作成

## 使用方法

```bash
# 基本的な処理
python3 lecture_pipeline.py --input sample.mp4 --out-dir ./output

# ChatGPT APIを使用した高度な処理
python3 lecture_pipeline.py --input sample.mp4 --use-chatgpt --out-dir ./output
```

## 設定ファイル

- `glossary.csv` - 用語辞書（専門用語の表記統一用）
- `.env` - OpenAI APIキーなどの設定
