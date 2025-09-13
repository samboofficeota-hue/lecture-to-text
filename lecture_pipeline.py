#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
動画/音声 → Whisper(ローカル,faster-whisper) で日本語文字起こし
→ 用語辞書で表記統一 → 未知語候補の抽出 → Markdownドラフト出力

使い方:
  1) 依存関係:
     pip install faster-whisper ffmpeg-python pandas unidic-lite fugashi
     ※ ffmpeg は別途インストールが必要
  2) 初回テンプレ: python lecture_pipeline.py --make-glossary-template
  3) 実行:
     python lecture_pipeline.py --input lecture.mp4 --glossary glossary.csv --model large-v3 --out-dir ./out
"""

import argparse
import os
import re
import sys
import csv
import json
from collections import Counter
from datetime import timedelta
from pathlib import Path

import pandas as pd
import ffmpeg
from faster_whisper import WhisperModel

# ChatGPT API統合
from text_enhancer import TextEnhancer
from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

# 形態素（簡易）: fugashi + unidic-lite
try:
    from fugashi import Tagger
    _tagger = Tagger()
except Exception:
    _tagger = None  # 形態素が使えない場合は正規表現のみで未知語候補を拾う

# -----------------------------
# ユーティリティ
# -----------------------------
def seconds_to_hhmmss(t: float) -> str:
    td = timedelta(seconds=int(t))
    # 00:00:00 形式
    s = str(td)
    return "00:" + s if len(s) <= 7 else s

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

# -----------------------------
# 音声抽出
# -----------------------------
def extract_audio(input_path: str, out_wav: str, sr: int = 16000):
    """
    動画/音声ファイルから mono/16kHz の wav を作る（高品質設定）
    """
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

# -----------------------------
# 文字起こし後処理
# -----------------------------
def postprocess_transcription(text: str) -> str:
    """
    文字起こしテキストの後処理
    - よくある誤認識パターンの修正
    - 句読点の調整
    - 専門用語の修正
    """
    # よくある誤認識パターンの修正
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
        "事業水行": "事業遂行",
        "バイクアクスる": "バイクアクス",
        "エルコード": "エルコード",
        "構測": "構築",
        "相影気": "相対的",
        "一区限管": "一括管理",
        "金入通し": "金融投資",
        "確保": "確保",
        "確讆": "確実",
        "通証儒": "投資",
        "保養師": "保有者",
        "調子": "投資",
        "ザイミューショーション": "サイミュレーション",
        "ザイミューショー": "サイミュレーション",
        "提議": "定義",
        "注束": "注目",
        "経役": "経営",
        "減速": "減損",
        "理想": "利益",
        "経験": "経営",
        "正じる": "正しい",
        "格好外全性": "確実性",
        "チャプターさん": "チャプター",
        "概念フレームワーク": "概念フレームワーク",
        "罪務法国": "財務報告",
        "当時者": "投資者",
        "企業性化": "企業価値",
        "企業化地": "企業価値",
        "解除": "開示",
        "ポジション": "ポジション",
        "性化": "価値",
        "解じ": "解釈",
        "構成予測": "構成要素",
        "各個法規": "各項目",
        "法規に刺激": "法規制",
        "特定期間": "特定期間",
        "銅石さん": "投資者",
        "辺道学": "変動",
        "法国主体": "報告主体",
        "5月間": "5年間",
        "オプション": "オプション",
        "とり引き": "取引",
        "リスク": "リスク",
        "開放": "解放",
        "通しの正化": "投資の成果",
        "報告したい": "報告主体",
        "期待された": "期待された",
        "実実": "実際",
        "確定": "確定",
        "キャッシュフロー": "キャッシュフロー",
        "裏付け": "裏付け",
        "事店": "事実",
        "事業通し": "事業投資",
        "先役": "責任",
        "水行通じて": "遂行を通じて",
        "エルコード": "エルコード",
        "リスクに構測": "リスクに構築",
        "どくりつ": "独立",
        "子さん": "資産",
        "拡足": "拡大",
        "事実を思って": "事実として",
        "キャッシュフロー": "キャッシュフロー",
        "角度": "観点",
        "もとついて": "基づいて",
        "相影気": "相対的",
        "しき": "識別",
        "一区限管": "一括管理",
        "金入通し": "金融投資",
        "事業水行上": "事業遂行上",
        "先役": "責任",
        "構成価値": "構成価値",
        "確保": "確保",
        "時間": "時価",
        "変動": "変動",
        "利益": "利益",
        "確讆": "確実",
        "通証儒": "投資",
        "事業目的": "事業目的",
        "構測": "構築",
        "保養師": "保有者",
        "値上がり": "値上がり",
        "期待": "期待",
        "調子": "投資",
        "価値": "価値",
        "変動事実": "変動事実",
        "思って": "として",
        "リスク": "リスク",
        "開放": "解放",
        "ものとなる": "ものとなる",
        "また": "また",
        "金融通締": "金融投資",
        "時間": "時価",
        "変動": "変動",
        "もとついて": "基づいて",
        "相影気": "相対的",
        "認識": "認識",
        "ため": "ため",
        "時間": "時価",
        "評価": "評価",
        "ザイミューショーション": "サイミュレーション",
        "ザイミューショー": "サイミュレーション",
        "構成様子": "構成要素",
        "提議": "定義",
        "注束": "注目",
        "項目": "項目",
        "認識": "認識",
        "きそ": "基礎",
        "経役": "経営",
        "減速": "減損",
        "少なくとも": "少なくとも",
        "一方": "一方",
        "理想": "利益",
        "経験": "経営",
        "提議": "定義",
        "見たした": "満たした",
        "項目": "項目",
        "罪務所表情": "財務諸表情",
        "認識対象": "認識対象",
        "正じる": "正しい",
        "くわえ": "加え",
        "一定程度": "一定程度",
        "発生可能性": "発生可能性",
        "格好外全性": "確実性",
        "求められる": "求められる",
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

# -----------------------------
# Whisper 文字起こし
# -----------------------------
def transcribe_with_whisper(
    wav_path: str,
    model_size: str = "large-v3",
    device: str = "auto",      # "cuda" / "cpu" / "auto"
    compute_type: str = "auto" # "float16" など
):
    """
    faster-whisper による文字起こし（高精度設定）
    戻り値: {"segments": [(start, end, text), ...], "text": 全文}
    """
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
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

    segs = []
    full_text_parts = []
    for s in segments:
        st = s.start if s.start else 0.0
        ed = s.end if s.end else st
        tx = (s.text or "").strip()
        if tx:
            # 基本的な後処理
            tx = postprocess_transcription(tx)
            segs.append((st, ed, tx))
            full_text_parts.append(tx)
    return {
        "segments": segs,
        "text": "\n".join(full_text_parts)
    }

# -----------------------------
# 用語辞書
# -----------------------------
def make_glossary_template(path: str = "glossary.csv"):
    if os.path.exists(path):
        print(f"[info] 既に存在: {path}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "normalized"])
        writer.writerow(["OpenAI", "OpenAI"])
        writer.writerow(["チャットGPT", "ChatGPT"])
        writer.writerow(["ラージビジョンモデル", "LVM"])
    print(f"[ok] テンプレ生成: {path}")

def load_glossary(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    mapping = {}
    for _, row in df.iterrows():
        term = str(row.get("term", "")).strip()
        norm = str(row.get("normalized", "")).strip()
        if term and norm:
            mapping[term] = norm
    return mapping

def apply_glossary(text: str, glossary: dict) -> str:
    """
    シンプル置換（長い語を先に置換して表記ゆれの衝突を減らす）
    """
    if not glossary:
        return text
    # 置換の安定化: 長い語から
    items = sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True)
    out = text
    for src, tgt in items:
        # 単純置換（日本語は単語境界が難しいため素直に）
        out = out.replace(src, tgt)
    return out

# -----------------------------
# 未知語候補の抽出
# -----------------------------
KANJI = r"\u4E00-\u9FFF"
KATAKANA = r"\u30A0-\u30FF\u31F0-\u31FF"
HIRAGANA = r"\u3040-\u309F"
ALNUM = r"A-Za-z0-9"

# 用語候補: (1) 漢字連 >1、(2) カタカナ語 >2、(3) 英数語 >2
CANDIDATE_RE = re.compile(
    rf"([{KANJI}]{{2,}}|[{KATAKANA}]{{3,}}|[{ALNUM}]{{3,}}(?:[-_][{ALNUM}]{{2,}})*)"
)

def tokenize(text: str):
    """ 形態素があればそれ、なければ空 """
    if _tagger is None:
        return []
    return [m.surface for m in _tagger(text)]

def collect_unknown_terms(text: str, glossary: dict, top_k: int = 200) -> pd.DataFrame:
    """
    辞書にない語の候補を単純抽出し、頻度順に返す
    - 形態素が使える場合は token もカウントに使用
    - 使えない場合は正規表現ヒットのカウントのみ
    """
    known = set(glossary.keys()) | set(glossary.values())
    counter = Counter()

    # 正規表現で候補収集
    for m in CANDIDATE_RE.finditer(text):
        w = m.group(0)
        if w not in known:
            counter[w] += 1

    # 形態素（任意）
    if _tagger is not None:
        for tk in tokenize(text):
            # ごく短いひらがなは除外
            if len(tk) <= 1:
                continue
            if tk not in known and CANDIDATE_RE.match(tk):
                counter[tk] += 1

    rows = [{"term": w, "freq": c} for w, c in counter.most_common(top_k)]
    return pd.DataFrame(rows)

# -----------------------------
# Markdownドラフト生成（雛形）
# -----------------------------
def make_textbook_markdown(title: str, normalized_text: str) -> str:
    """
    ChatGPT プロジェクトでの整形前に “たたき台” を用意。
    章は時間で機械的にではなく、段落ごとに区切っておく。
    """
    paras = [p.strip() for p in normalized_text.split("\n") if p.strip()]
    body = "\n\n".join([f"- {p}" for p in paras[:2000]])  # 安全に上限

    md = f"""# {title}

## 学習目標（下書き）
- 講義内容の全体像を理解する
- キーワードと専門用語の定義を把握する
- 主要トピック間の関係を説明できる

## 講義本文（段落メモ）
{body}

## 用語集（追って整備）
- 例）PBR：株価純資産倍率
- 例）ルーブリック：評価観点表

## 確認問題（案）
1. 本講義の主題は何か？
2. 重要用語を3つ挙げて定義せよ。
3. 講義で示された事例は何を示唆するか？

"""
    return md

# -----------------------------
# メイン処理
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="入力ファイル（動画 mp4 / 音声 wav, mp3 など）")
    ap.add_argument("--out-dir", default="./output")
    ap.add_argument("--glossary", default="glossary.csv")
    ap.add_argument("--model", default=WHISPER_MODEL, help="Whisperモデル: large-v3 / medium / small ...")
    ap.add_argument("--device", default=WHISPER_DEVICE, help="auto/cpu/cuda")
    ap.add_argument("--compute-type", default=WHISPER_COMPUTE_TYPE, help="auto/float16/int8 など")
    ap.add_argument("--title", default="講義録")
    ap.add_argument("--make-glossary-template", action="store_true", help="辞書テンプレCSVを出力して終了")
    ap.add_argument("--use-chatgpt", action="store_true", help="ChatGPT APIを使用してテキストを改善")
    ap.add_argument("--skip-chatgpt", action="store_true", help="ChatGPT APIをスキップして従来の処理のみ実行")
    args = ap.parse_args()

    if args.make_glossary_template:
        make_glossary_template(args.glossary)
        sys.exit(0)

    if not args.input:
        print("[error] --input を指定してください")
        sys.exit(1)

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    # 1) 音声抽出
    wav_path = str(out_dir / "audio.wav")
    print("[step] 音声抽出:", wav_path)
    extract_audio(args.input, wav_path, sr=16000)

    # 2) 文字起こし
    print("[step] 文字起こし（faster-whisper）...")
    tr = transcribe_with_whisper(
        wav_path=wav_path,
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    raw_text = tr["text"]
    (out_dir / "transcript.raw.txt").write_text(raw_text, encoding="utf-8")
    print("[ok] transcript.raw.txt 書き出し")

    # 3) 用語辞書の適用
    glossary = load_glossary(args.glossary)
    norm_text = apply_glossary(raw_text, glossary)
    (out_dir / "transcript.norm.txt").write_text(norm_text, encoding="utf-8")
    print("[ok] transcript.norm.txt 書き出し（表記統一後）")

    # 4) 未知語候補の抽出
    df_unknown = collect_unknown_terms(norm_text, glossary, top_k=300)
    df_unknown.to_csv(out_dir / "unknown_terms.csv", index=False, encoding="utf-8")
    print("[ok] unknown_terms.csv 書き出し（辞書育成用）")

    # 5) ChatGPT API統合処理
    if args.use_chatgpt and not args.skip_chatgpt:
        try:
            print("[step] ChatGPT APIでテキスト改善を開始...")
            enhancer = TextEnhancer()
            
            # フルパイプライン実行
            results = enhancer.process_full_pipeline(raw_text, args.title)
            
            # 結果を保存
            enhanced_text = results["enhanced_text"]
            full_transcript = results["full_transcript"]
            technical_terms = results["technical_terms"]
            
            # 改善されたテキストを保存
            (out_dir / "transcript.enhanced.txt").write_text(enhanced_text, encoding="utf-8")
            print("[ok] transcript.enhanced.txt 書き出し（ChatGPT改善後）")
            
            # フル講義録を保存
            (out_dir / "full_transcript.md").write_text(full_transcript, encoding="utf-8")
            print("[ok] full_transcript.md 書き出し（フル講義録）")
            
            # 専門用語リストを保存
            terms_df = pd.DataFrame({"term": technical_terms})
            terms_df.to_csv(out_dir / "technical_terms.csv", index=False, encoding="utf-8")
            print("[ok] technical_terms.csv 書き出し（専門用語リスト）")
            
        except Exception as e:
            print(f"[警告] ChatGPT API処理でエラー: {e}")
            print("[info] 従来の処理のみで続行します")
            # フォールバック：従来の処理
            md = make_textbook_markdown(args.title, norm_text)
            (out_dir / "textbook_draft.md").write_text(md, encoding="utf-8")
            print("[ok] textbook_draft.md 書き出し")
    else:
        # 従来の処理
        md = make_textbook_markdown(args.title, norm_text)
        (out_dir / "textbook_draft.md").write_text(md, encoding="utf-8")
        print("[ok] textbook_draft.md 書き出し")

    print("\n[done] 出力先:", str(out_dir.resolve()))
    print(" - transcript.raw.txt   : Whisper生テキスト")
    print(" - transcript.norm.txt  : 辞書適用後テキスト")
    print(" - unknown_terms.csv    : 未知語候補（頻度つき）")
    if args.use_chatgpt and not args.skip_chatgpt:
        print(" - transcript.enhanced.txt : ChatGPT改善後テキスト")
        print(" - full_transcript.md      : フル講義録")
        print(" - technical_terms.csv     : 専門用語リスト")
    else:
        print(" - textbook_draft.md       : 授業用下書き（Markdown）")

if __name__ == "__main__":
    main()