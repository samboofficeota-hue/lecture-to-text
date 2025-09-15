"""
テキスト処理ユーティリティ

テキストの処理に関する共通機能を提供します。
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from .logging import get_logger

logger = get_logger(__name__)


class TextUtils:
    """テキスト処理ユーティリティ"""
    
    # 日本語の文字クラス
    KANJI = r"\u4E00-\u9FFF"
    KATAKANA = r"\u30A0-\u30FF\u31F0-\u31FF"
    HIRAGANA = r"\u3040-\u309F"
    ALNUM = r"A-Za-z0-9"
    
    # 用語候補の正規表現
    CANDIDATE_RE = re.compile(
        rf"([{KANJI}]{{2,}}|[{KATAKANA}]{{3,}}|[{ALNUM}]{{3,}}(?:[-_][{ALNUM}]{{2,}})*)"
    )
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        テキストをクリーニング
        
        Args:
            text: クリーニングするテキスト
            
        Returns:
            str: クリーニング済みテキスト
        """
        # 重複する空白を削除
        text = re.sub(r'\s+', ' ', text)
        
        # 重複する句読点を修正
        text = re.sub(r'、\s*、', '、', text)
        text = re.sub(r'。\s*。', '。', text)
        
        # 先頭・末尾の空白を削除
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_terms(text: str, min_length: int = 2) -> List[str]:
        """
        テキストから用語候補を抽出
        
        Args:
            text: 抽出するテキスト
            min_length: 最小文字数
            
        Returns:
            List[str]: 用語候補のリスト
        """
        terms = []
        
        # 正規表現で候補を抽出
        for match in TextUtils.CANDIDATE_RE.finditer(text):
            term = match.group(0)
            if len(term) >= min_length:
                terms.append(term)
        
        return terms
    
    @staticmethod
    def extract_terms_with_frequency(
        text: str, 
        min_length: int = 2,
        top_k: int = 200
    ) -> List[Tuple[str, int]]:
        """
        テキストから用語候補を頻度付きで抽出
        
        Args:
            text: 抽出するテキスト
            min_length: 最小文字数
            top_k: 上位k個
            
        Returns:
            List[Tuple[str, int]]: (用語, 頻度)のリスト
        """
        terms = TextUtils.extract_terms(text, min_length)
        counter = Counter(terms)
        return counter.most_common(top_k)
    
    @staticmethod
    def apply_corrections(
        text: str, 
        corrections: Dict[str, str]
    ) -> str:
        """
        テキストに修正を適用
        
        Args:
            text: 修正するテキスト
            corrections: 修正辞書
            
        Returns:
            str: 修正済みテキスト
        """
        result = text
        
        # 長い語から先に置換（表記ゆれの衝突を防ぐ）
        sorted_corrections = sorted(
            corrections.items(), 
            key=lambda x: len(x[0]), 
            reverse=True
        )
        
        for wrong, correct in sorted_corrections:
            result = result.replace(wrong, correct)
        
        return result
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        テキストを文に分割
        
        Args:
            text: 分割するテキスト
            
        Returns:
            List[str]: 文のリスト
        """
        # 日本語の文分割（簡易版）
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    @staticmethod
    def split_into_paragraphs(text: str) -> List[str]:
        """
        テキストを段落に分割
        
        Args:
            text: 分割するテキスト
            
        Returns:
            List[str]: 段落のリスト
        """
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, Any]:
        """
        テキストの統計情報を取得
        
        Args:
            text: 統計を取得するテキスト
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        # 基本的な統計
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        paragraph_count = len(TextUtils.split_into_paragraphs(text))
        sentence_count = len(TextUtils.split_into_sentences(text))
        
        # 文字種別の統計
        kanji_count = len(re.findall(TextUtils.KANJI, text))
        katakana_count = len(re.findall(TextUtils.KATAKANA, text))
        hiragana_count = len(re.findall(TextUtils.HIRAGANA, text))
        alnum_count = len(re.findall(TextUtils.ALNUM, text))
        
        return {
            'char_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'kanji_count': kanji_count,
            'katakana_count': katakana_count,
            'hiragana_count': hiragana_count,
            'alnum_count': alnum_count,
            'avg_words_per_sentence': word_count / sentence_count if sentence_count > 0 else 0,
            'avg_sentences_per_paragraph': sentence_count / paragraph_count if paragraph_count > 0 else 0
        }
    
    @staticmethod
    def validate_text_quality(text: str) -> Dict[str, Any]:
        """
        テキストの品質を検証
        
        Args:
            text: 検証するテキスト
            
        Returns:
            Dict[str, Any]: 品質評価結果
        """
        stats = TextUtils.get_text_statistics(text)
        
        # 品質スコアを計算（簡易版）
        quality_score = 0.0
        
        # 文字数による評価
        if stats['char_count'] > 100:
            quality_score += 0.2
        if stats['char_count'] > 500:
            quality_score += 0.2
        if stats['char_count'] > 1000:
            quality_score += 0.2
        
        # 文の長さによる評価
        avg_words_per_sentence = stats['avg_words_per_sentence']
        if 5 <= avg_words_per_sentence <= 30:
            quality_score += 0.2
        elif 3 <= avg_words_per_sentence <= 50:
            quality_score += 0.1
        
        # 段落の長さによる評価
        avg_sentences_per_paragraph = stats['avg_sentences_per_paragraph']
        if 2 <= avg_sentences_per_paragraph <= 10:
            quality_score += 0.2
        
        # 文字種の多様性による評価
        char_diversity = len(set(text)) / len(text) if text else 0
        if char_diversity > 0.1:
            quality_score += 0.2
        
        return {
            'quality_score': min(quality_score, 1.0),
            'statistics': stats,
            'recommendations': TextUtils._get_quality_recommendations(stats, quality_score)
        }
    
    @staticmethod
    def _get_quality_recommendations(
        stats: Dict[str, Any], 
        quality_score: float
    ) -> List[str]:
        """
        品質改善の推奨事項を取得
        
        Args:
            stats: 統計情報
            quality_score: 品質スコア
            
        Returns:
            List[str]: 推奨事項のリスト
        """
        recommendations = []
        
        if stats['char_count'] < 100:
            recommendations.append("テキストが短すぎます。より詳細な内容を追加してください。")
        
        if stats['avg_words_per_sentence'] < 5:
            recommendations.append("文が短すぎます。より詳細な説明を追加してください。")
        elif stats['avg_words_per_sentence'] > 50:
            recommendations.append("文が長すぎます。文を分割することを検討してください。")
        
        if stats['avg_sentences_per_paragraph'] < 2:
            recommendations.append("段落が短すぎます。関連する文をまとめてください。")
        elif stats['avg_sentences_per_paragraph'] > 15:
            recommendations.append("段落が長すぎます。段落を分割することを検討してください。")
        
        if quality_score < 0.5:
            recommendations.append("全体的な品質が低いです。内容の見直しを検討してください。")
        
        return recommendations


# 便利な関数
def clean_text(text: str) -> str:
    """テキストをクリーニング"""
    return TextUtils.clean_text(text)


def extract_terms(text: str, min_length: int = 2) -> List[str]:
    """テキストから用語候補を抽出"""
    return TextUtils.extract_terms(text, min_length)
