"""
自動辞書生成

テキストから自動的に辞書を生成します。
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from datetime import datetime

from ...utils.logging import get_logger
from ...utils.text_utils import TextUtils
from .glossary_manager import GlossaryManager

logger = get_logger(__name__)


class AutoGlossaryGenerator:
    """自動辞書生成"""
    
    def __init__(self, glossary_manager: Optional[GlossaryManager] = None):
        """
        自動辞書生成を初期化
        
        Args:
            glossary_manager: 辞書管理
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        
        # 日本語の文字クラス
        self.KANJI = r"\u4E00-\u9FFF"
        self.KATAKANA = r"\u30A0-\u30FF\u31F0-\u31FF"
        self.HIRAGANA = r"\u3040-\u309F"
        self.ALNUM = r"A-Za-z0-9"
        
        # 用語候補の正規表現
        self.CANDIDATE_RE = re.compile(
            rf"([{self.KANJI}]{{2,}}|[{self.KATAKANA}]{{3,}}|[{self.ALNUM}]{{3,}}(?:[-_][{self.ALNUM}]{{2,}})*)"
        )
    
    def generate_glossary_from_text(
        self, 
        text: str, 
        domain: str,
        min_frequency: int = 2,
        min_length: int = 2,
        max_terms: int = 1000
    ) -> Dict[str, str]:
        """
        テキストから辞書を生成
        
        Args:
            text: 処理するテキスト
            domain: 分野
            min_frequency: 最小頻度
            min_length: 最小文字数
            max_terms: 最大用語数
            
        Returns:
            Dict[str, str]: 生成された辞書
        """
        try:
            # 用語候補を抽出
            terms = self._extract_candidate_terms(text, min_length)
            
            # 頻度を計算
            term_frequency = Counter(terms)
            
            # 頻度フィルタリング
            filtered_terms = {
                term: freq for term, freq in term_frequency.items()
                if freq >= min_frequency
            }
            
            # 正規化された用語を生成
            glossary = {}
            for term, freq in filtered_terms.items():
                normalized = self._normalize_term(term, domain)
                if normalized != term:
                    glossary[term] = normalized
            
            # 用語数を制限
            if len(glossary) > max_terms:
                # 頻度順にソートして上位を選択
                sorted_terms = sorted(
                    glossary.items(),
                    key=lambda x: term_frequency.get(x[0], 0),
                    reverse=True
                )
                glossary = dict(sorted_terms[:max_terms])
            
            logger.info(f"Generated glossary: {domain} ({len(glossary)} terms)")
            return glossary
            
        except Exception as e:
            logger.error(f"Failed to generate glossary: {e}")
            return {}
    
    def generate_glossary_from_pdf(
        self, 
        pdf_content: str, 
        domain: str,
        min_frequency: int = 2,
        min_length: int = 2,
        max_terms: int = 1000
    ) -> Dict[str, str]:
        """
        PDF内容から辞書を生成
        
        Args:
            pdf_content: PDF内容
            domain: 分野
            min_frequency: 最小頻度
            min_length: 最小文字数
            max_terms: 最大用語数
            
        Returns:
            Dict[str, str]: 生成された辞書
        """
        return self.generate_glossary_from_text(
            pdf_content, domain, min_frequency, min_length, max_terms
        )
    
    def generate_glossary_from_lecture(
        self, 
        lecture_text: str, 
        domain: str,
        existing_glossary: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        講義テキストから辞書を生成
        
        Args:
            lecture_text: 講義テキスト
            domain: 分野
            existing_glossary: 既存の辞書
            
        Returns:
            Dict[str, str]: 生成された辞書
        """
        try:
            # 既存の辞書を読み込み
            if existing_glossary is None:
                existing_glossary = self.glossary_manager.load_glossary(domain)
            
            # 用語候補を抽出
            terms = self._extract_candidate_terms(lecture_text)
            
            # 既知の用語を除外
            known_terms = set(existing_glossary.keys()) | set(existing_glossary.values())
            unknown_terms = [term for term in terms if term not in known_terms]
            
            # 頻度を計算
            term_frequency = Counter(unknown_terms)
            
            # 新しい辞書を生成
            new_glossary = {}
            for term, freq in term_frequency.items():
                if freq >= 2:  # 最低2回出現
                    normalized = self._normalize_term(term, domain)
                    if normalized != term:
                        new_glossary[term] = normalized
            
            # 既存の辞書とマージ
            merged_glossary = {**existing_glossary, **new_glossary}
            
            logger.info(f"Generated lecture glossary: {domain} ({len(new_glossary)} new terms)")
            return merged_glossary
            
        except Exception as e:
            logger.error(f"Failed to generate lecture glossary: {e}")
            return existing_glossary or {}
    
    def suggest_corrections(
        self, 
        text: str, 
        domain: str
    ) -> List[Tuple[str, str, float]]:
        """
        修正候補を提案
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            List[Tuple[str, str, float]]: (誤認識, 修正候補, 信頼度)のリスト
        """
        try:
            # 既存の辞書を読み込み
            glossary = self.glossary_manager.load_glossary(domain)
            
            suggestions = []
            
            # テキストを文に分割
            sentences = TextUtils.split_into_sentences(text)
            
            for sentence in sentences:
                # 用語候補を抽出
                terms = self._extract_candidate_terms(sentence)
                
                for term in terms:
                    # 既知の用語と類似するものを検索
                    similar_terms = self._find_similar_terms(term, glossary)
                    
                    for similar_term, similarity in similar_terms:
                        if similarity > 0.8:  # 高い類似度
                            suggestions.append((term, similar_term, similarity))
            
            # 信頼度順にソート
            suggestions.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Generated suggestions: {domain} ({len(suggestions)} suggestions)")
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    def _extract_candidate_terms(
        self, 
        text: str, 
        min_length: int = 2
    ) -> List[str]:
        """
        用語候補を抽出
        
        Args:
            text: 処理するテキスト
            min_length: 最小文字数
            
        Returns:
            List[str]: 用語候補のリスト
        """
        terms = []
        
        # 正規表現で候補を抽出
        for match in self.CANDIDATE_RE.finditer(text):
            term = match.group(0)
            if len(term) >= min_length:
                terms.append(term)
        
        return terms
    
    def _normalize_term(
        self, 
        term: str, 
        domain: str
    ) -> str:
        """
        用語を正規化
        
        Args:
            term: 用語
            domain: 分野
            
        Returns:
            str: 正規化された用語
        """
        # 基本的な正規化
        normalized = term.strip()
        
        # 分野別の正規化ルール
        if domain == "会計・財務":
            normalized = self._normalize_accounting_term(normalized)
        elif domain == "技術・工学":
            normalized = self._normalize_technical_term(normalized)
        elif domain == "経済学":
            normalized = self._normalize_economics_term(normalized)
        
        return normalized
    
    def _normalize_accounting_term(self, term: str) -> str:
        """会計・財務用語の正規化"""
        # 既存の修正ルールを適用
        corrections = {
            "罪務": "財務",
            "罪有者": "所有者",
            "創数": "総数",
            "順利益": "純利益",
            "順次": "純資産",
            "基隣": "基準",
            "正化": "成果",
            "通し": "投資",
            "事業水行": "事業遂行",
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
            "求められる": "求められる"
        }
        
        return corrections.get(term, term)
    
    def _normalize_technical_term(self, term: str) -> str:
        """技術・工学分野用語の正規化"""
        # 技術分野の正規化ルール（簡易実装）
        return term
    
    def _normalize_economics_term(self, term: str) -> str:
        """経済学分野用語の正規化"""
        # 経済学分野の正規化ルール（簡易実装）
        return term
    
    def _find_similar_terms(
        self, 
        term: str, 
        glossary: Dict[str, str]
    ) -> List[Tuple[str, float]]:
        """
        類似用語を検索
        
        Args:
            term: 用語
            glossary: 辞書
            
        Returns:
            List[Tuple[str, float]]: (類似用語, 類似度)のリスト
        """
        similar_terms = []
        
        for known_term in glossary.keys():
            similarity = self._calculate_similarity(term, known_term)
            if similarity > 0.5:  # 閾値
                similar_terms.append((known_term, similarity))
        
        return similar_terms
    
    def _calculate_similarity(self, term1: str, term2: str) -> float:
        """
        用語間の類似度を計算
        
        Args:
            term1: 用語1
            term2: 用語2
            
        Returns:
            float: 類似度（0.0-1.0）
        """
        # 簡易的な類似度計算（実際の実装では、より高度なアルゴリズムを使用）
        if term1 == term2:
            return 1.0
        
        # 文字列の長さの差を考慮
        len_diff = abs(len(term1) - len(term2))
        max_len = max(len(term1), len(term2))
        
        if max_len == 0:
            return 0.0
        
        # 共通部分の長さを計算
        common_chars = 0
        for char in term1:
            if char in term2:
                common_chars += 1
        
        # 類似度を計算
        similarity = (common_chars * 2) / (len(term1) + len(term2))
        
        # 長さの差によるペナルティ
        length_penalty = len_diff / max_len
        similarity = similarity * (1 - length_penalty)
        
        return similarity
