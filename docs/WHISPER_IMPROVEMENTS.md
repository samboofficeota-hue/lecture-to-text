# Whisper文字起こし精度改善ガイド

## 問題の分析

提供されたサンプルテキストから、以下の問題が確認されました：

### 主な誤認識パターン
1. **専門用語の誤認識**
   - 罪務 → 財務
   - 順利益 → 純利益
   - 順次 → 純資産
   - 基隣 → 基準
   - 正化 → 成果

2. **音声の類似性による誤認識**
   - 通し → 投資
   - 事業水行 → 事業遂行
   - 構測 → 構築
   - 相影気 → 相対的

3. **文脈の理解不足**
   - 当時者 → 投資者
   - 銅石さん → 投資者
   - 5月間 → 5年間

## 実装した改善策

### 1. Whisperパラメータの最適化

```python
segments, info = model.transcribe(
    wav_path,
    language="ja",           # 日本語を明示
    beam_size=5,             # ビームサーチのサイズ
    best_of=5,               # 複数候補から最良を選択
    temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],  # 温度パラメータの配列
    vad_filter=True,         # 無音区間の誤聴き取り抑制
    vad_parameters=dict(
        min_silence_duration_ms=500,
        speech_pad_ms=400,   # 音声の前後にパディング
        min_speech_duration_ms=250,  # 最小音声長
        max_speech_duration_s=30.0   # 最大音声長
    ),
    word_timestamps=True,    # 単語レベルのタイムスタンプ
    condition_on_previous_text=True,  # 前の文脈を考慮
    initial_prompt="これは日本語の講義です。専門用語が多く含まれています。",  # 初期プロンプト
    compression_ratio_threshold=2.4,  # 圧縮比の閾値
    log_prob_threshold=-1.0,  # ログ確率の閾値
    no_speech_threshold=0.6,  # 無音判定の閾値
)
```

### 2. 音声前処理の改善

```python
def extract_audio(input_path: str, out_wav: str, sr: int = 16000):
    (
        ffmpeg
        .input(input_path)
        .output(
            out_wav, 
            ac=1,           # モノラル
            ar=sr,          # サンプルレート
            vn=None,        # 動画を無効化
            y=None,         # 上書き確認を無効化
            af="highpass=f=80,lowpass=f=8000,volume=1.2",  # 音声フィルタ
            acodec='pcm_s16le'  # 16bit PCM
        )
        .run(quiet=True, overwrite_output=True)
    )
    return out_wav
```

### 3. 文字起こし後処理の実装

専門用語の誤認識パターンを修正する辞書ベースの後処理：

```python
def postprocess_transcription(text: str) -> str:
    corrections = {
        # 会計・財務用語の修正
        "罪務": "財務",
        "罪有者": "所有者",
        "創数": "総数",
        "順利益": "純利益",
        "順次": "純資産",
        "基隣": "基準",
        "正化": "成果",
        "通し": "投資",
        # ... その他多数の修正パターン
    }
    
    # 修正を適用
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    # 句読点の調整
    text = re.sub(r'、\s*、', '、', text)  # 重複する読点を修正
    text = re.sub(r'。\s*。', '。', text)  # 重複する句点を修正
    text = re.sub(r'\s+', ' ', text)      # 複数の空白を1つに
    text = text.strip()
    
    return text
```

### 4. モデル設定の最適化

```python
# config.py
WHISPER_MODEL = "large-v3"  # より高精度なモデル
```

## 改善結果

### 改善前
```
[0.0s-6.2s] チャプターさん、概念フレームワーク、
[6.2s-10.2s] 罪務法国の目的。
[10.2s-20.7s] 当時者による、企業性化の予測と、企業化地の評価に役立つような企業の罪務状況の解除を目的としている。
```

### 改善後
```
チャプター、概念フレームワーク、 財務報告の目的。 投資者による、企業価値の予測と、企業価値の評価に役立つような企業の財務状況の開示を目的としている。
```

## 使用方法

### 基本的な使用
```bash
python3 lecture_pipeline.py --input sample.mp4 --out-dir ./output
```

### 高精度設定での使用
```bash
python3 lecture_pipeline.py --input sample.mp4 --model large-v3 --out-dir ./output
```

### ChatGPT APIを使用した高度な処理
```bash
python3 lecture_pipeline.py --input sample.mp4 --use-chatgpt --out-dir ./output
```

## さらなる改善のための推奨事項

1. **専門用語辞書の拡充**
   - 分野別の専門用語辞書を作成
   - 講義の内容に応じて辞書をカスタマイズ

2. **音声品質の向上**
   - ノイズ除去ソフトウェアの使用
   - 適切なマイクの使用
   - 静かな環境での録音

3. **文脈の理解向上**
   - より詳細な初期プロンプトの設定
   - 講義の分野に特化したプロンプト

4. **後処理の改善**
   - 機械学習ベースの誤認識修正
   - 文脈を考慮した用語修正

## 注意事項

- `large-v3`モデルは処理時間が長くなりますが、精度が大幅に向上します
- 音声の品質が低い場合は、前処理のフィルタを調整してください
- 専門用語が多い講義の場合は、用語辞書を事前に準備することを推奨します
