"""
RAG（Retrieval-Augmented Generation）インターフェース

知識ベースを活用したテキスト修正・改善を行う抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from ..models.processing_result import ProcessingResult


@dataclass
class RAGConfig:
    """RAG設定"""
    knowledge_base_path: Optional[str] = None
    domain: Optional[str] = None
    use_mygpt: bool = True
    use_chatgpt: bool = True
    confidence_threshold: float = 0.8
    max_context_length: int = 4000
    temperature: float = 0.3


@dataclass
class KnowledgeItem:
    """知識アイテム"""
    id: str
    content: str
    domain: str
    metadata: Dict[str, Any]
    confidence: float = 1.0


class RAGInterface(ABC):
    """RAGの抽象インターフェース"""
    
    @abstractmethod
    def process_with_rag(
        self, 
        text: str,
        config: Optional[RAGConfig] = None
    ) -> str:
        """
        RAGを使用してテキストを処理する
        
        Args:
            text: 処理するテキスト
            config: RAG設定
            
        Returns:
            str: 処理済みテキスト
        """
        pass
    
    @abstractmethod
    def retrieve_knowledge(
        self, 
        query: str,
        domain: Optional[str] = None,
        top_k: int = 5
    ) -> List[KnowledgeItem]:
        """
        知識ベースから関連情報を検索する
        
        Args:
            query: 検索クエリ
            domain: 分野
            top_k: 取得する上位k個
            
        Returns:
            List[KnowledgeItem]: 関連知識アイテム
        """
        pass
    
    @abstractmethod
    def add_knowledge(
        self, 
        knowledge_item: KnowledgeItem
    ) -> bool:
        """
        知識ベースに新しい知識を追加する
        
        Args:
            knowledge_item: 追加する知識アイテム
            
        Returns:
            bool: 追加の成功/失敗
        """
        pass
    
    @abstractmethod
    def update_knowledge(
        self, 
        knowledge_id: str,
        updated_content: str
    ) -> bool:
        """
        既存の知識を更新する
        
        Args:
            knowledge_id: 更新する知識のID
            updated_content: 更新内容
            
        Returns:
            bool: 更新の成功/失敗
        """
        pass
    
    @abstractmethod
    def search_similar_terms(
        self, 
        term: str,
        domain: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        類似用語を検索する
        
        Args:
            term: 検索する用語
            domain: 分野
            
        Returns:
            List[Tuple[str, float]]: (用語, 類似度)のリスト
        """
        pass
    
    @abstractmethod
    def unify_concepts(
        self, 
        text: str,
        domain: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        概念・理論の統一性を保つ
        
        Args:
            text: 処理するテキスト
            domain: 分野
            context: 文脈情報
            
        Returns:
            str: 概念統一済みテキスト
        """
        pass
    
    @abstractmethod
    def validate_terminology(
        self, 
        text: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        専門用語の妥当性を検証する
        
        Args:
            text: 検証するテキスト
            domain: 分野
            
        Returns:
            Dict[str, Any]: 検証結果
        """
        pass
    
    @abstractmethod
    def get_domain_knowledge(
        self, 
        domain: str
    ) -> List[KnowledgeItem]:
        """
        分野別の知識を取得する
        
        Args:
            domain: 分野
            
        Returns:
            List[KnowledgeItem]: 分野別知識
        """
        pass
