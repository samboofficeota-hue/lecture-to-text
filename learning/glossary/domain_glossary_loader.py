"""
分野別辞書ローダー

分野別の辞書を読み込みます。
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from ...utils.logging import get_logger
from .glossary_manager import GlossaryManager

logger = get_logger(__name__)


class DomainGlossaryLoader:
    """分野別辞書ローダー"""
    
    def __init__(self, glossary_manager: Optional[GlossaryManager] = None):
        """
        分野別辞書ローダーを初期化
        
        Args:
            glossary_manager: 辞書管理
        """
        self.glossary_manager = glossary_manager or GlossaryManager()
        
        # 分野別の辞書ファイルパス
        self.domain_glossaries = {
            "会計・財務": "accounting_finance.csv",
            "技術・工学": "engineering.csv",
            "経済学": "economics.csv",
            "法律": "law.csv",
            "医学": "medicine.csv",
            "教育": "education.csv",
            "ビジネス": "business.csv"
        }
    
    def load_domain_glossary(
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
        return self.glossary_manager.load_glossary(domain, force_reload)
    
    def load_all_domain_glossaries(
        self, 
        force_reload: bool = False
    ) -> Dict[str, Dict[str, str]]:
        """
        全分野の辞書を読み込み
        
        Args:
            force_reload: 強制再読み込み
            
        Returns:
            Dict[str, Dict[str, str]]: 分野別辞書
        """
        all_glossaries = {}
        
        for domain in self.domain_glossaries.keys():
            try:
                glossary = self.load_domain_glossary(domain, force_reload)
                all_glossaries[domain] = glossary
                logger.info(f"Loaded domain glossary: {domain} ({len(glossary)} terms)")
            except Exception as e:
                logger.error(f"Failed to load domain glossary {domain}: {e}")
                all_glossaries[domain] = {}
        
        return all_glossaries
    
    def get_available_domains(self) -> List[str]:
        """
        利用可能な分野一覧を取得
        
        Returns:
            List[str]: 分野のリスト
        """
        return list(self.domain_glossaries.keys())
    
    def get_domain_glossary_path(self, domain: str) -> Optional[str]:
        """
        分野別辞書ファイルのパスを取得
        
        Args:
            domain: 分野
            
        Returns:
            Optional[str]: ファイルパス
        """
        if domain in self.domain_glossaries:
            return self.domain_glossaries[domain]
        return None
    
    def create_domain_glossary(
        self, 
        domain: str, 
        initial_terms: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        分野別辞書を作成
        
        Args:
            domain: 分野
            initial_terms: 初期用語
            
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            if initial_terms is None:
                initial_terms = {}
            
            return self.glossary_manager.save_glossary(domain, initial_terms)
            
        except Exception as e:
            logger.error(f"Failed to create domain glossary: {e}")
            return False
    
    def merge_domain_glossaries(
        self, 
        target_domain: str, 
        source_domains: List[str]
    ) -> bool:
        """
        複数の分野辞書をマージ
        
        Args:
            target_domain: マージ先の分野
            source_domains: マージ元の分野
            
        Returns:
            bool: マージの成功/失敗
        """
        try:
            merged_glossary = {}
            
            for source_domain in source_domains:
                source_glossary = self.load_domain_glossary(source_domain)
                merged_glossary.update(source_glossary)
            
            return self.glossary_manager.save_glossary(target_domain, merged_glossary)
            
        except Exception as e:
            logger.error(f"Failed to merge domain glossaries: {e}")
            return False
    
    def get_domain_glossary_stats(self) -> Dict[str, Any]:
        """
        分野別辞書の統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        stats = {}
        
        for domain in self.domain_glossaries.keys():
            try:
                domain_stats = self.glossary_manager.get_glossary_stats(domain)
                stats[domain] = domain_stats
            except Exception as e:
                logger.error(f"Failed to get stats for domain {domain}: {e}")
                stats[domain] = {'error': str(e)}
        
        return stats
