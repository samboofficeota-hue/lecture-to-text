"""
分野検出

テキストの分野を自動検出します。
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

from ...utils.logging import get_logger
from ...utils.text_utils import TextUtils

logger = get_logger(__name__)


class DomainDetector:
    """分野検出"""
    
    def __init__(self):
        """分野検出を初期化"""
        # 分野別のキーワード
        self.domain_keywords = {
            "会計・財務": [
                "財務", "会計", "損益", "貸借", "資産", "負債", "資本", "収益", "費用",
                "キャッシュフロー", "バランスシート", "損益計算書", "財務諸表",
                "監査", "税務", "予算", "決算", "投資", "リスク", "リターン"
            ],
            "技術・工学": [
                "技術", "工学", "システム", "ソフトウェア", "ハードウェア", "アルゴリズム",
                "データベース", "ネットワーク", "セキュリティ", "プログラミング",
                "開発", "設計", "実装", "テスト", "デバッグ", "最適化"
            ],
            "経済学": [
                "経済", "経済学", "市場", "需要", "供給", "価格", "価値", "効率",
                "ミクロ経済", "マクロ経済", "GDP", "インフレ", "デフレ", "失業率",
                "金利", "為替", "貿易", "投資", "消費", "貯蓄"
            ],
            "法律": [
                "法律", "法", "条項", "規則", "規制", "契約", "権利", "義務",
                "責任", "損害", "賠償", "訴訟", "判決", "判例", "法解釈",
                "憲法", "民法", "商法", "刑法", "行政法"
            ],
            "医学": [
                "医学", "医療", "診断", "治療", "症状", "疾患", "病院", "医師",
                "看護", "薬物", "手術", "検査", "予防", "健康", "生命", "身体"
            ],
            "教育": [
                "教育", "学習", "授業", "講義", "学生", "教師", "学校", "大学",
                "研究", "論文", "知識", "技能", "能力", "評価", "試験", "資格"
            ],
            "ビジネス": [
                "ビジネス", "経営", "マーケティング", "営業", "販売", "顧客",
                "商品", "サービス", "価格", "利益", "売上", "コスト", "戦略",
                "組織", "管理", "リーダーシップ", "チーム", "プロジェクト"
            ]
        }
        
        # 分野別の正規表現パターン
        self.domain_patterns = {
            "会計・財務": [
                r"財務諸表", r"損益計算書", r"貸借対照表", r"キャッシュフロー",
                r"監査", r"税務", r"予算", r"決算", r"投資", r"リスク"
            ],
            "技術・工学": [
                r"システム", r"ソフトウェア", r"ハードウェア", r"アルゴリズム",
                r"データベース", r"ネットワーク", r"セキュリティ", r"プログラミング"
            ],
            "経済学": [
                r"ミクロ経済", r"マクロ経済", r"GDP", r"インフレ", r"デフレ",
                r"失業率", r"金利", r"為替", r"貿易", r"投資"
            ],
            "法律": [
                r"法律", r"条項", r"規則", r"規制", r"契約", r"権利", r"義務",
                r"責任", r"損害", r"賠償", r"訴訟", r"判決"
            ],
            "医学": [
                r"医学", r"医療", r"診断", r"治療", r"症状", r"疾患", r"病院",
                r"医師", r"看護", r"薬物", r"手術", r"検査"
            ],
            "教育": [
                r"教育", r"学習", r"授業", r"講義", r"学生", r"教師", r"学校",
                r"大学", r"研究", r"論文", r"知識", r"技能"
            ],
            "ビジネス": [
                r"ビジネス", r"経営", r"マーケティング", r"営業", r"販売", r"顧客",
                r"商品", r"サービス", r"価格", r"利益", r"売上", r"コスト"
            ]
        }
    
    def detect_domain(
        self, 
        text: str, 
        threshold: float = 0.1
    ) -> Tuple[str, float]:
        """
        テキストの分野を検出
        
        Args:
            text: 処理するテキスト
            threshold: 閾値
            
        Returns:
            Tuple[str, float]: (分野, 信頼度)
        """
        try:
            # 各分野のスコアを計算
            domain_scores = {}
            
            for domain, keywords in self.domain_keywords.items():
                score = self._calculate_keyword_score(text, keywords)
                domain_scores[domain] = score
            
            # 正規表現パターンも考慮
            for domain, patterns in self.domain_patterns.items():
                pattern_score = self._calculate_pattern_score(text, patterns)
                domain_scores[domain] = max(domain_scores.get(domain, 0), pattern_score)
            
            # 最高スコアの分野を選択
            if domain_scores:
                best_domain = max(domain_scores.items(), key=lambda x: x[1])
                if best_domain[1] >= threshold:
                    logger.info(f"Detected domain: {best_domain[0]} (confidence: {best_domain[1]:.3f})")
                    return best_domain
                else:
                    logger.warning(f"Domain detection confidence too low: {best_domain[1]:.3f}")
                    return "不明", 0.0
            else:
                logger.warning("No domain detected")
                return "不明", 0.0
                
        except Exception as e:
            logger.error(f"Failed to detect domain: {e}")
            return "不明", 0.0
    
    def detect_multiple_domains(
        self, 
        text: str, 
        top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        複数の分野を検出
        
        Args:
            text: 処理するテキスト
            top_k: 上位k個の分野
            
        Returns:
            List[Tuple[str, float]]: (分野, 信頼度)のリスト
        """
        try:
            # 各分野のスコアを計算
            domain_scores = {}
            
            for domain, keywords in self.domain_keywords.items():
                score = self._calculate_keyword_score(text, keywords)
                domain_scores[domain] = score
            
            # 正規表現パターンも考慮
            for domain, patterns in self.domain_patterns.items():
                pattern_score = self._calculate_pattern_score(text, patterns)
                domain_scores[domain] = max(domain_scores.get(domain, 0), pattern_score)
            
            # スコア順にソート
            sorted_domains = sorted(
                domain_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_domains[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to detect multiple domains: {e}")
            return []
    
    def get_domain_confidence(
        self, 
        text: str, 
        domain: str
    ) -> float:
        """
        特定の分野の信頼度を取得
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            float: 信頼度
        """
        try:
            if domain not in self.domain_keywords:
                return 0.0
            
            # キーワードスコアを計算
            keyword_score = self._calculate_keyword_score(text, self.domain_keywords[domain])
            
            # 正規表現パターンスコアを計算
            pattern_score = 0.0
            if domain in self.domain_patterns:
                pattern_score = self._calculate_pattern_score(text, self.domain_patterns[domain])
            
            # 高い方のスコアを返す
            return max(keyword_score, pattern_score)
            
        except Exception as e:
            logger.error(f"Failed to get domain confidence: {e}")
            return 0.0
    
    def _calculate_keyword_score(
        self, 
        text: str, 
        keywords: List[str]
    ) -> float:
        """
        キーワードスコアを計算
        
        Args:
            text: 処理するテキスト
            keywords: キーワードリスト
            
        Returns:
            float: スコア
        """
        if not keywords:
            return 0.0
        
        # テキストを小文字に変換
        text_lower = text.lower()
        
        # キーワードの出現回数をカウント
        keyword_counts = Counter()
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            if count > 0:
                keyword_counts[keyword] = count
        
        # スコアを計算
        total_keywords = len(keywords)
        found_keywords = len(keyword_counts)
        total_occurrences = sum(keyword_counts.values())
        
        # キーワードの種類数と出現回数の重み付き平均
        diversity_score = found_keywords / total_keywords
        frequency_score = min(total_occurrences / 10, 1.0)  # 最大1.0
        
        return (diversity_score * 0.7 + frequency_score * 0.3)
    
    def _calculate_pattern_score(
        self, 
        text: str, 
        patterns: List[str]
    ) -> float:
        """
        正規表現パターンスコアを計算
        
        Args:
            text: 処理するテキスト
            patterns: 正規表現パターンリスト
            
        Returns:
            float: スコア
        """
        if not patterns:
            return 0.0
        
        # パターンのマッチ数をカウント
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match_count += 1
        
        # スコアを計算
        return match_count / len(patterns)
    
    def add_domain_keywords(
        self, 
        domain: str, 
        keywords: List[str]
    ) -> bool:
        """
        分野のキーワードを追加
        
        Args:
            domain: 分野
            keywords: キーワードリスト
            
        Returns:
            bool: 追加の成功/失敗
        """
        try:
            if domain not in self.domain_keywords:
                self.domain_keywords[domain] = []
            
            self.domain_keywords[domain].extend(keywords)
            self.domain_keywords[domain] = list(set(self.domain_keywords[domain]))  # 重複を削除
            
            logger.info(f"Added keywords to domain {domain}: {len(keywords)} keywords")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add domain keywords: {e}")
            return False
    
    def add_domain_patterns(
        self, 
        domain: str, 
        patterns: List[str]
    ) -> bool:
        """
        分野の正規表現パターンを追加
        
        Args:
            domain: 分野
            patterns: 正規表現パターンリスト
            
        Returns:
            bool: 追加の成功/失敗
        """
        try:
            if domain not in self.domain_patterns:
                self.domain_patterns[domain] = []
            
            self.domain_patterns[domain].extend(patterns)
            self.domain_patterns[domain] = list(set(self.domain_patterns[domain]))  # 重複を削除
            
            logger.info(f"Added patterns to domain {domain}: {len(patterns)} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add domain patterns: {e}")
            return False
    
    def get_available_domains(self) -> List[str]:
        """
        利用可能な分野一覧を取得
        
        Returns:
            List[str]: 分野のリスト
        """
        return list(self.domain_keywords.keys())
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        分野の情報を取得
        
        Args:
            domain: 分野
            
        Returns:
            Dict[str, Any]: 分野情報
        """
        return {
            'domain': domain,
            'keywords': self.domain_keywords.get(domain, []),
            'patterns': self.domain_patterns.get(domain, []),
            'keyword_count': len(self.domain_keywords.get(domain, [])),
            'pattern_count': len(self.domain_patterns.get(domain, []))
        }
