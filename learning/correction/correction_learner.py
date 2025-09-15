"""
修正学習

ユーザーの修正から学習します。
"""

import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path

from ...utils.logging import get_logger
from ...utils.text_utils import TextUtils

logger = get_logger(__name__)


class CorrectionLearner:
    """修正学習"""
    
    def __init__(self, learning_data_dir: str = "./data/learning_data"):
        """
        修正学習を初期化
        
        Args:
            learning_data_dir: 学習データディレクトリ
        """
        self.learning_data_dir = Path(learning_data_dir)
        self.learning_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 修正パターンのキャッシュ
        self._correction_patterns: Dict[str, Dict[str, Any]] = {}
        self._last_loaded: Optional[datetime] = None
    
    def learn_from_correction(
        self, 
        original_text: str, 
        corrected_text: str, 
        domain: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        修正から学習
        
        Args:
            original_text: 元のテキスト
            corrected_text: 修正されたテキスト
            domain: 分野
            context: 文脈情報
            
        Returns:
            bool: 学習の成功/失敗
        """
        try:
            # 修正パターンを抽出
            patterns = self._extract_correction_patterns(original_text, corrected_text)
            
            if not patterns:
                logger.warning("No correction patterns found")
                return False
            
            # 学習データを保存
            learning_data = {
                'timestamp': datetime.now().isoformat(),
                'domain': domain,
                'original_text': original_text,
                'corrected_text': corrected_text,
                'patterns': patterns,
                'context': context or {}
            }
            
            # 学習データファイルに追加
            learning_file = self.learning_data_dir / f"{domain}_corrections.jsonl"
            with open(learning_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(learning_data, ensure_ascii=False) + '\n')
            
            # 修正パターンを更新
            self._update_correction_patterns(domain, patterns)
            
            logger.info(f"Learned from correction: {domain} ({len(patterns)} patterns)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to learn from correction: {e}")
            return False
    
    def get_correction_suggestions(
        self, 
        text: str, 
        domain: str
    ) -> List[Tuple[str, str, float]]:
        """
        修正候補を取得
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            List[Tuple[str, str, float]]: (誤認識, 修正候補, 信頼度)のリスト
        """
        try:
            # 修正パターンを読み込み
            patterns = self._load_correction_patterns(domain)
            
            suggestions = []
            
            # テキストを文に分割
            sentences = TextUtils.split_into_sentences(text)
            
            for sentence in sentences:
                # 各修正パターンを適用
                for pattern, correction_data in patterns.items():
                    if pattern in sentence:
                        confidence = correction_data.get('confidence', 0.0)
                        corrected_sentence = sentence.replace(pattern, correction_data['correction'])
                        suggestions.append((pattern, correction_data['correction'], confidence))
            
            # 信頼度順にソート
            suggestions.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Generated correction suggestions: {domain} ({len(suggestions)} suggestions)")
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get correction suggestions: {e}")
            return []
    
    def apply_learned_corrections(
        self, 
        text: str, 
        domain: str
    ) -> str:
        """
        学習した修正を適用
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            str: 修正適用済みテキスト
        """
        try:
            # 修正パターンを読み込み
            patterns = self._load_correction_patterns(domain)
            
            result = text
            
            # 信頼度の高い順に修正を適用
            sorted_patterns = sorted(
                patterns.items(),
                key=lambda x: x[1].get('confidence', 0.0),
                reverse=True
            )
            
            for pattern, correction_data in sorted_patterns:
                if pattern in result:
                    result = result.replace(pattern, correction_data['correction'])
            
            logger.info(f"Applied learned corrections: {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply learned corrections: {e}")
            return text
    
    def get_learning_stats(self, domain: str) -> Dict[str, Any]:
        """
        学習統計を取得
        
        Args:
            domain: 分野
            
        Returns:
            Dict[str, Any]: 学習統計
        """
        try:
            learning_file = self.learning_data_dir / f"{domain}_corrections.jsonl"
            
            if not learning_file.exists():
                return {
                    'domain': domain,
                    'total_corrections': 0,
                    'total_patterns': 0,
                    'last_learning': None
                }
            
            # 学習データを読み込み
            corrections = []
            with open(learning_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        corrections.append(json.loads(line))
            
            # 統計を計算
            total_corrections = len(corrections)
            total_patterns = sum(len(c.get('patterns', [])) for c in corrections)
            last_learning = max(
                (c.get('timestamp', '') for c in corrections),
                default=None
            )
            
            return {
                'domain': domain,
                'total_corrections': total_corrections,
                'total_patterns': total_patterns,
                'last_learning': last_learning
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning stats: {e}")
            return {'domain': domain, 'error': str(e)}
    
    def _extract_correction_patterns(
        self, 
        original_text: str, 
        corrected_text: str
    ) -> List[Dict[str, Any]]:
        """
        修正パターンを抽出
        
        Args:
            original_text: 元のテキスト
            corrected_text: 修正されたテキスト
            
        Returns:
            List[Dict[str, Any]]: 修正パターンのリスト
        """
        patterns = []
        
        # 文に分割
        original_sentences = TextUtils.split_into_sentences(original_text)
        corrected_sentences = TextUtils.split_into_sentences(corrected_text)
        
        # 文の数が同じ場合のみ処理
        if len(original_sentences) == len(corrected_sentences):
            for orig_sent, corr_sent in zip(original_sentences, corrected_sentences):
                if orig_sent != corr_sent:
                    # 単語レベルで差分を検出
                    orig_words = orig_sent.split()
                    corr_words = corr_sent.split()
                    
                    # 単語の数が同じ場合のみ処理
                    if len(orig_words) == len(corr_words):
                        for orig_word, corr_word in zip(orig_words, corr_words):
                            if orig_word != corr_word:
                                patterns.append({
                                    'original': orig_word,
                                    'correction': corr_word,
                                    'context': orig_sent,
                                    'confidence': 1.0
                                })
        
        return patterns
    
    def _update_correction_patterns(
        self, 
        domain: str, 
        patterns: List[Dict[str, Any]]
    ):
        """
        修正パターンを更新
        
        Args:
            domain: 分野
            patterns: 修正パターン
        """
        if domain not in self._correction_patterns:
            self._correction_patterns[domain] = {}
        
        for pattern in patterns:
            original = pattern['original']
            correction = pattern['correction']
            
            if original in self._correction_patterns[domain]:
                # 既存のパターンの信頼度を更新
                existing = self._correction_patterns[domain][original]
                existing['confidence'] = (existing['confidence'] + pattern['confidence']) / 2
                existing['count'] = existing.get('count', 1) + 1
            else:
                # 新しいパターンを追加
                self._correction_patterns[domain][original] = {
                    'correction': correction,
                    'confidence': pattern['confidence'],
                    'count': 1
                }
    
    def _load_correction_patterns(self, domain: str) -> Dict[str, Any]:
        """
        修正パターンを読み込み
        
        Args:
            domain: 分野
            
        Returns:
            Dict[str, Any]: 修正パターン
        """
        if domain not in self._correction_patterns:
            self._correction_patterns[domain] = {}
        
        return self._correction_patterns[domain]
