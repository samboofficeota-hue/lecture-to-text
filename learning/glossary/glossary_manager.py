"""
辞書管理

辞書の管理と操作を行います。
"""

import csv
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

from ...utils.logging import get_logger
from ...utils.text_utils import TextUtils

logger = get_logger(__name__)


class GlossaryManager:
    """辞書管理"""
    
    def __init__(self, glossary_dir: str = "./data/glossaries"):
        """
        辞書管理を初期化
        
        Args:
            glossary_dir: 辞書ディレクトリ
        """
        self.glossary_dir = Path(glossary_dir)
        self.glossary_dir.mkdir(parents=True, exist_ok=True)
        
        # 辞書キャッシュ
        self._glossary_cache: Dict[str, Dict[str, str]] = {}
        self._last_modified: Dict[str, datetime] = {}
    
    def load_glossary(
        self, 
        domain: str, 
        force_reload: bool = False
    ) -> Dict[str, str]:
        """
        分野別辞書を読み込み
        
        Args:
            domain: 分野
            force_reload: 強制再読み込み
            
        Returns:
            Dict[str, str]: 辞書
        """
        glossary_path = self.glossary_dir / f"{domain}.csv"
        
        # キャッシュをチェック
        if not force_reload and domain in self._glossary_cache:
            if glossary_path.exists():
                mtime = datetime.fromtimestamp(glossary_path.stat().st_mtime)
                if mtime <= self._last_modified.get(domain, datetime.min):
                    return self._glossary_cache[domain]
        
        # 辞書を読み込み
        glossary = {}
        if glossary_path.exists():
            try:
                with open(glossary_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        term = row.get('term', '').strip()
                        normalized = row.get('normalized', '').strip()
                        if term and normalized:
                            glossary[term] = normalized
                
                logger.info(f"Glossary loaded: {domain} ({len(glossary)} terms)")
                
            except Exception as e:
                logger.error(f"Failed to load glossary: {e}")
        
        # キャッシュを更新
        self._glossary_cache[domain] = glossary
        if glossary_path.exists():
            self._last_modified[domain] = datetime.fromtimestamp(glossary_path.stat().st_mtime)
        
        return glossary
    
    def save_glossary(
        self, 
        domain: str, 
        glossary: Dict[str, str]
    ) -> bool:
        """
        分野別辞書を保存
        
        Args:
            domain: 分野
            glossary: 辞書
            
        Returns:
            bool: 保存の成功/失敗
        """
        try:
            glossary_path = self.glossary_dir / f"{domain}.csv"
            
            with open(glossary_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['term', 'normalized'])
                
                for term, normalized in sorted(glossary.items()):
                    writer.writerow([term, normalized])
            
            # キャッシュを更新
            self._glossary_cache[domain] = glossary
            self._last_modified[domain] = datetime.now()
            
            logger.info(f"Glossary saved: {domain} ({len(glossary)} terms)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save glossary: {e}")
            return False
    
    def add_term(
        self, 
        domain: str, 
        term: str, 
        normalized: str
    ) -> bool:
        """
        用語を追加
        
        Args:
            domain: 分野
            term: 用語
            normalized: 正規化された用語
            
        Returns:
            bool: 追加の成功/失敗
        """
        glossary = self.load_glossary(domain)
        glossary[term] = normalized
        
        return self.save_glossary(domain, glossary)
    
    def remove_term(
        self, 
        domain: str, 
        term: str
    ) -> bool:
        """
        用語を削除
        
        Args:
            domain: 分野
            term: 用語
            
        Returns:
            bool: 削除の成功/失敗
        """
        glossary = self.load_glossary(domain)
        
        if term in glossary:
            del glossary[term]
            return self.save_glossary(domain, glossary)
        
        return False
    
    def update_term(
        self, 
        domain: str, 
        term: str, 
        normalized: str
    ) -> bool:
        """
        用語を更新
        
        Args:
            domain: 分野
            term: 用語
            normalized: 正規化された用語
            
        Returns:
            bool: 更新の成功/失敗
        """
        glossary = self.load_glossary(domain)
        
        if term in glossary:
            glossary[term] = normalized
            return self.save_glossary(domain, glossary)
        
        return False
    
    def get_term(
        self, 
        domain: str, 
        term: str
    ) -> Optional[str]:
        """
        用語の正規化された形を取得
        
        Args:
            domain: 分野
            term: 用語
            
        Returns:
            Optional[str]: 正規化された用語
        """
        glossary = self.load_glossary(domain)
        return glossary.get(term)
    
    def search_terms(
        self, 
        domain: str, 
        query: str
    ) -> List[Tuple[str, str]]:
        """
        用語を検索
        
        Args:
            domain: 分野
            query: 検索クエリ
            
        Returns:
            List[Tuple[str, str]]: (用語, 正規化された用語)のリスト
        """
        glossary = self.load_glossary(domain)
        
        results = []
        query_lower = query.lower()
        
        for term, normalized in glossary.items():
            if query_lower in term.lower() or query_lower in normalized.lower():
                results.append((term, normalized))
        
        return results
    
    def merge_glossaries(
        self, 
        domain: str, 
        other_glossary: Dict[str, str]
    ) -> bool:
        """
        辞書をマージ
        
        Args:
            domain: 分野
            other_glossary: マージする辞書
            
        Returns:
            bool: マージの成功/失敗
        """
        glossary = self.load_glossary(domain)
        
        # 既存の辞書に新しい用語を追加
        for term, normalized in other_glossary.items():
            if term not in glossary:
                glossary[term] = normalized
        
        return self.save_glossary(domain, glossary)
    
    def apply_glossary(
        self, 
        text: str, 
        domain: str
    ) -> str:
        """
        辞書を適用してテキストを正規化
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            str: 正規化されたテキスト
        """
        glossary = self.load_glossary(domain)
        
        if not glossary:
            return text
        
        # 長い語から先に置換（表記ゆれの衝突を防ぐ）
        sorted_glossary = sorted(
            glossary.items(), 
            key=lambda x: len(x[0]), 
            reverse=True
        )
        
        result = text
        for term, normalized in sorted_glossary:
            result = result.replace(term, normalized)
        
        return result
    
    def extract_unknown_terms(
        self, 
        text: str, 
        domain: str, 
        top_k: int = 200
    ) -> List[Tuple[str, int]]:
        """
        未知語候補を抽出
        
        Args:
            text: 処理するテキスト
            domain: 分野
            top_k: 抽出する上位k個
            
        Returns:
            List[Tuple[str, int]]: (用語, 頻度)のリスト
        """
        glossary = self.load_glossary(domain)
        known_terms = set(glossary.keys()) | set(glossary.values())
        
        # 用語候補を抽出
        terms = TextUtils.extract_terms(text)
        
        # 既知の用語を除外
        unknown_terms = [term for term in terms if term not in known_terms]
        
        # 頻度を計算
        from collections import Counter
        counter = Counter(unknown_terms)
        
        return counter.most_common(top_k)
    
    def get_glossary_stats(self, domain: str) -> Dict[str, Any]:
        """
        辞書の統計情報を取得
        
        Args:
            domain: 分野
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        glossary = self.load_glossary(domain)
        
        return {
            'domain': domain,
            'total_terms': len(glossary),
            'unique_terms': len(set(glossary.keys())),
            'unique_normalized': len(set(glossary.values())),
            'last_modified': self._last_modified.get(domain),
            'file_path': str(self.glossary_dir / f"{domain}.csv")
        }
    
    def list_domains(self) -> List[str]:
        """
        利用可能な分野一覧を取得
        
        Returns:
            List[str]: 分野のリスト
        """
        domains = []
        
        for csv_file in self.glossary_dir.glob("*.csv"):
            domain = csv_file.stem
            domains.append(domain)
        
        return sorted(domains)
    
    def backup_glossary(self, domain: str) -> bool:
        """
        辞書をバックアップ
        
        Args:
            domain: 分野
            
        Returns:
            bool: バックアップの成功/失敗
        """
        try:
            glossary_path = self.glossary_dir / f"{domain}.csv"
            backup_path = self.glossary_dir / f"{domain}.backup.{int(datetime.now().timestamp())}.csv"
            
            if glossary_path.exists():
                import shutil
                shutil.copy2(glossary_path, backup_path)
                logger.info(f"Glossary backed up: {domain}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to backup glossary: {e}")
            return False
    
    def restore_glossary(self, domain: str, backup_file: str) -> bool:
        """
        辞書を復元
        
        Args:
            domain: 分野
            backup_file: バックアップファイル
            
        Returns:
            bool: 復元の成功/失敗
        """
        try:
            backup_path = Path(backup_file)
            glossary_path = self.glossary_dir / f"{domain}.csv"
            
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, glossary_path)
                
                # キャッシュをクリア
                if domain in self._glossary_cache:
                    del self._glossary_cache[domain]
                
                logger.info(f"Glossary restored: {domain}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restore glossary: {e}")
            return False
