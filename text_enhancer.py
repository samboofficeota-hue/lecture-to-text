#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT APIを使用したテキスト改善機能
- 専門用語の補強
- 文章表現のブラッシュアップ
- フルバージョン講義録の生成
"""

import re
import json
from typing import List, Dict, Tuple
from openai import OpenAI
from config import OPENAI_API_KEY, CHATGPT_MODEL, CHATGPT_TEMPERATURE, CHATGPT_MAX_TOKENS

class TextEnhancer:
    def __init__(self):
        """ChatGPT APIクライアントを初期化"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルまたは環境変数を確認してください。")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = CHATGPT_MODEL
        self.temperature = CHATGPT_TEMPERATURE
        self.max_tokens = CHATGPT_MAX_TOKENS

    def extract_technical_terms(self, text: str) -> List[str]:
        """
        テキストから専門用語候補を抽出
        """
        prompt = f"""
以下の講義テキストから、専門用語や固有名詞を抽出してください。
特に以下の条件に該当する用語を優先してください：

1. 技術用語（IT、ビジネス、学術分野など）
2. 固有名詞（会社名、人名、製品名など）
3. 略語（3文字以上のアルファベット）
4. カタカナ語（3文字以上）
5. 漢字熟語（2文字以上）

抽出した用語をJSON配列形式で出力してください。
例：["ChatGPT", "OpenAI", "機械学習", "API", "データベース"]

テキスト：
{text[:2000]}...
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            # JSON形式の部分を抽出
            json_match = re.search(r'\[.*?\]', result, re.DOTALL)
            if json_match:
                terms = json.loads(json_match.group())
                return [term for term in terms if isinstance(term, str) and len(term) > 1]
            return []
            
        except Exception as e:
            print(f"[警告] 専門用語抽出でエラー: {e}")
            return []

    def enhance_transcription(self, raw_text: str, technical_terms: List[str] = None) -> str:
        """
        文字起こしテキストを改善
        - 専門用語の補強
        - 文章表現のブラッシュアップ
        """
        if technical_terms is None:
            technical_terms = self.extract_technical_terms(raw_text)
        
        terms_context = ", ".join(technical_terms[:20]) if technical_terms else "なし"
        
        prompt = f"""
以下の講義の文字起こしテキストを、読みやすい講義録に改善してください。

【改善のポイント】
1. 専門用語の表記を統一・正確にする
2. 話し言葉を書き言葉に適切に変換
3. 文の流れを自然にする
4. 誤字脱字を修正
5. 段落構成を整理

【専門用語候補】
{terms_context}

【元のテキスト】
{raw_text}

【改善されたテキスト】
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[警告] テキスト改善でエラー: {e}")
            return raw_text

    def create_full_transcript(self, enhanced_text: str, title: str = "講義録") -> str:
        """
        フルバージョンの講義録を生成
        - 章立て
        - 学習目標
        - 用語集
        - 確認問題
        """
        prompt = f"""
以下の講義内容を基に、完成度の高い講義録を作成してください。

【講義タイトル】
{title}

【講義内容】
{enhanced_text}

【出力形式】
以下の構造でMarkdown形式で出力してください：

# {title}

## 学習目標
- 目標1
- 目標2
- 目標3

## 講義内容

### 1. 導入
（講義の導入部分）

### 2. 主要トピック1
（内容の詳細）

### 3. 主要トピック2
（内容の詳細）

### 4. まとめ
（講義のまとめ）

## 重要用語集
- 用語1: 定義
- 用語2: 定義

## 確認問題
1. 問題1
2. 問題2
3. 問題3

## 参考資料
- 参考資料1
- 参考資料2
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[警告] フル講義録生成でエラー: {e}")
            # フォールバック：基本的な構造で返す
            return f"""# {title}

## 講義内容
{enhanced_text}

## 重要用語集
（用語集は後で整備してください）

## 確認問題
（確認問題は後で作成してください）
"""

    def process_full_pipeline(self, raw_text: str, title: str = "講義録") -> Dict[str, str]:
        """
        フルパイプライン実行
        1. 専門用語抽出
        2. テキスト改善
        3. フル講義録生成
        """
        print("[step] 専門用語を抽出中...")
        technical_terms = self.extract_technical_terms(raw_text)
        print(f"[ok] {len(technical_terms)}個の専門用語を抽出")
        
        print("[step] テキストを改善中...")
        enhanced_text = self.enhance_transcription(raw_text, technical_terms)
        print("[ok] テキスト改善完了")
        
        print("[step] フル講義録を生成中...")
        full_transcript = self.create_full_transcript(enhanced_text, title)
        print("[ok] フル講義録生成完了")
        
        return {
            "technical_terms": technical_terms,
            "enhanced_text": enhanced_text,
            "full_transcript": full_transcript
        }
