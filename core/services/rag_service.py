"""
RAGサービス

RAG（Retrieval-Augmented Generation）に関するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any, List, Tuple
import time

from ..interfaces.rag_interface import RAGInterface, RAGConfig, KnowledgeItem
from ..models.processing_result import ProcessingResult


class RAGService:
    """RAGサービス"""
    
    def __init__(self, rag_interface: RAGInterface):
        """
        RAGサービスを初期化
        
        Args:
            rag_interface: RAGインターフェース
        """
        self.rag_interface = rag_interface
    
    def process_with_rag(
        self, 
        text: str,
        domain: str,
        config: Optional[RAGConfig] = None
    ) -> str:
        """
        RAGを使用してテキストを処理する
        
        Args:
            text: 処理するテキスト
            domain: 分野
            config: RAG設定
            
        Returns:
            str: 処理済みテキスト
        """
        if config is None:
            config = RAGConfig(domain=domain)
        
        start_time = time.time()
        
        try:
            result = self.rag_interface.process_with_rag(text, config)
            processing_time = time.time() - start_time
            
            # 処理時間をログに記録
            print(f"RAG processing completed in {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            print(f"RAG processing failed: {e}")
            return text  # フォールバック
    
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
        return self.rag_interface.retrieve_knowledge(query, domain, top_k)
    
    def add_knowledge(
        self, 
        content: str,
        domain: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        知識ベースに新しい知識を追加する
        
        Args:
            content: 知識内容
            domain: 分野
            metadata: メタデータ
            
        Returns:
            bool: 追加の成功/失敗
        """
        if metadata is None:
            metadata = {}
        
        knowledge_item = KnowledgeItem(
            id=f"knowledge_{int(time.time())}",
            content=content,
            domain=domain,
            metadata=metadata
        )
        
        return self.rag_interface.add_knowledge(knowledge_item)
    
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
        return self.rag_interface.search_similar_terms(term, domain)
    
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
        return self.rag_interface.unify_concepts(text, domain, context)
    
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
        return self.rag_interface.validate_terminology(text, domain)
    
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
        return self.rag_interface.get_domain_knowledge(domain)
    
    def process_lecture_with_rag(
        self, 
        processing_result: ProcessingResult,
        domain: str,
        config: Optional[RAGConfig] = None
    ) -> ProcessingResult:
        """
        講義録をRAGで処理する
        
        Args:
            processing_result: 処理結果
            domain: 分野
            config: RAG設定
            
        Returns:
            ProcessingResult: RAG処理済み結果
        """
        if config is None:
            config = RAGConfig(domain=domain)
        
        # RAG処理を実行
        enhanced_text = self.process_with_rag(
            processing_result.processed_text, domain, config
        )
        
        # 結果を更新
        processing_result.enhanced_text = enhanced_text
        processing_result.add_metadata('rag_processed', True)
        processing_result.add_metadata('rag_domain', domain)
        
        return processing_result
