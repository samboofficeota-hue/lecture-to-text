"""
RAG管理

RAGシステムの管理を行います。
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from ...utils.logging import get_logger
from .knowledge_base import KnowledgeBase
from .mygpt_integration import MyGPTIntegration

logger = get_logger(__name__)


class RAGManager:
    """RAG管理"""
    
    def __init__(
        self, 
        knowledge_base: Optional[KnowledgeBase] = None,
        mygpt_integration: Optional[MyGPTIntegration] = None
    ):
        """
        RAG管理を初期化
        
        Args:
            knowledge_base: 知識ベース
            mygpt_integration: My GPTs連携
        """
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.mygpt_integration = mygpt_integration or MyGPTIntegration()
        
        # RAG設定
        self.rag_config = {
            'max_context_length': 4000,
            'similarity_threshold': 0.7,
            'max_retrieved_items': 5,
            'enable_mygpt': True
        }
    
    def process_with_rag(
        self, 
        text: str, 
        domain: str,
        query: Optional[str] = None
    ) -> str:
        """
        RAGを使用してテキストを処理
        
        Args:
            text: 処理するテキスト
            domain: 分野
            query: 検索クエリ
            
        Returns:
            str: 処理済みテキスト
        """
        try:
            if query is None:
                query = f"{domain}分野の専門知識を活用してテキストを改善"
            
            # 関連知識を検索
            relevant_knowledge = self.retrieve_relevant_knowledge(query, domain)
            
            if not relevant_knowledge:
                logger.warning(f"No relevant knowledge found for domain: {domain}")
                return text
            
            # 知識を統合してテキストを改善
            enhanced_text = self._integrate_knowledge(text, relevant_knowledge, domain)
            
            logger.info(f"RAG processing completed: {domain}")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            return text
    
    def retrieve_relevant_knowledge(
        self, 
        query: str, 
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        関連知識を検索
        
        Args:
            query: 検索クエリ
            domain: 分野
            
        Returns:
            List[Dict[str, Any]]: 関連知識のリスト
        """
        try:
            # ローカル知識ベースから検索
            local_knowledge = self.knowledge_base.search(query, domain)
            
            # My GPTsから検索（有効な場合）
            mygpt_knowledge = []
            if self.rag_config.get('enable_mygpt', True):
                mygpt_knowledge = self.mygpt_integration.search_knowledge(query, domain)
            
            # 知識を統合
            all_knowledge = local_knowledge + mygpt_knowledge
            
            # 類似度でソート
            sorted_knowledge = sorted(
                all_knowledge,
                key=lambda x: x.get('similarity', 0.0),
                reverse=True
            )
            
            # 上位の知識を返す
            max_items = self.rag_config.get('max_retrieved_items', 5)
            return sorted_knowledge[:max_items]
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant knowledge: {e}")
            return []
    
    def add_knowledge(
        self, 
        content: str, 
        domain: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        知識を追加
        
        Args:
            content: 知識内容
            domain: 分野
            metadata: メタデータ
            
        Returns:
            bool: 追加の成功/失敗
        """
        try:
            # ローカル知識ベースに追加
            local_success = self.knowledge_base.add_item(content, domain, metadata)
            
            # My GPTsに追加（有効な場合）
            mygpt_success = True
            if self.rag_config.get('enable_mygpt', True):
                mygpt_success = self.mygpt_integration.add_knowledge(content, domain, metadata)
            
            success = local_success and mygpt_success
            if success:
                logger.info(f"Knowledge added: {domain}")
            else:
                logger.warning(f"Partial knowledge addition: {domain}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            return False
    
    def update_knowledge(
        self, 
        knowledge_id: str, 
        content: str, 
        domain: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        知識を更新
        
        Args:
            knowledge_id: 知識ID
            content: 知識内容
            domain: 分野
            metadata: メタデータ
            
        Returns:
            bool: 更新の成功/失敗
        """
        try:
            # ローカル知識ベースを更新
            local_success = self.knowledge_base.update_item(knowledge_id, content, domain, metadata)
            
            # My GPTsを更新（有効な場合）
            mygpt_success = True
            if self.rag_config.get('enable_mygpt', True):
                mygpt_success = self.mygpt_integration.update_knowledge(knowledge_id, content, domain, metadata)
            
            success = local_success and mygpt_success
            if success:
                logger.info(f"Knowledge updated: {knowledge_id}")
            else:
                logger.warning(f"Partial knowledge update: {knowledge_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update knowledge: {e}")
            return False
    
    def delete_knowledge(
        self, 
        knowledge_id: str, 
        domain: str
    ) -> bool:
        """
        知識を削除
        
        Args:
            knowledge_id: 知識ID
            domain: 分野
            
        Returns:
            bool: 削除の成功/失敗
        """
        try:
            # ローカル知識ベースから削除
            local_success = self.knowledge_base.delete_item(knowledge_id, domain)
            
            # My GPTsから削除（有効な場合）
            mygpt_success = True
            if self.rag_config.get('enable_mygpt', True):
                mygpt_success = self.mygpt_integration.delete_knowledge(knowledge_id, domain)
            
            success = local_success and mygpt_success
            if success:
                logger.info(f"Knowledge deleted: {knowledge_id}")
            else:
                logger.warning(f"Partial knowledge deletion: {knowledge_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {e}")
            return False
    
    def get_knowledge_stats(self, domain: str) -> Dict[str, Any]:
        """
        知識ベースの統計情報を取得
        
        Args:
            domain: 分野
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        try:
            # ローカル知識ベースの統計
            local_stats = self.knowledge_base.get_stats(domain)
            
            # My GPTsの統計（有効な場合）
            mygpt_stats = {}
            if self.rag_config.get('enable_mygpt', True):
                mygpt_stats = self.mygpt_integration.get_stats(domain)
            
            return {
                'domain': domain,
                'local_knowledge': local_stats,
                'mygpt_knowledge': mygpt_stats,
                'total_items': local_stats.get('total_items', 0) + mygpt_stats.get('total_items', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge stats: {e}")
            return {'domain': domain, 'error': str(e)}
    
    def _integrate_knowledge(
        self, 
        text: str, 
        knowledge: List[Dict[str, Any]], 
        domain: str
    ) -> str:
        """
        知識を統合してテキストを改善
        
        Args:
            text: 元のテキスト
            knowledge: 関連知識
            domain: 分野
            
        Returns:
            str: 改善されたテキスト
        """
        try:
            if not knowledge:
                return text
            
            # 知識を統合
            integrated_knowledge = "\n".join([
                f"- {item.get('content', '')}" for item in knowledge
            ])
            
            # プロンプトを構築
            prompt = f"""
以下の{domain}分野のテキストについて、提供された知識を活用して品質を向上させてください。

元のテキスト:
{text}

関連知識:
{integrated_knowledge}

改善のポイント:
1. 専門用語の正確性
2. 概念の統一性
3. 文脈の適切性
4. 全体的な品質

改善されたテキストを出力してください。
"""
            
            # My GPTsを使用してテキストを改善
            if self.rag_config.get('enable_mygpt', True):
                enhanced_text = self.mygpt_integration.process_text(prompt, domain)
                return enhanced_text
            else:
                # フォールバック：元のテキストを返す
                return text
                
        except Exception as e:
            logger.error(f"Failed to integrate knowledge: {e}")
            return text
    
    def configure_rag(self, config: Dict[str, Any]) -> bool:
        """
        RAG設定を更新
        
        Args:
            config: 設定
            
        Returns:
            bool: 更新の成功/失敗
        """
        try:
            self.rag_config.update(config)
            logger.info("RAG configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure RAG: {e}")
            return False
    
    def get_rag_config(self) -> Dict[str, Any]:
        """
        RAG設定を取得
        
        Returns:
            Dict[str, Any]: RAG設定
        """
        return self.rag_config.copy()
    
    def enable_mygpt(self, enable: bool = True) -> bool:
        """
        My GPTs連携を有効/無効化
        
        Args:
            enable: 有効化フラグ
            
        Returns:
            bool: 設定の成功/失敗
        """
        try:
            self.rag_config['enable_mygpt'] = enable
            logger.info(f"My GPTs integration {'enabled' if enable else 'disabled'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure My GPTs: {e}")
            return False
