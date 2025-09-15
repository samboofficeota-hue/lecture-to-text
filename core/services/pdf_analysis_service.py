"""
PDF分析サービス

PDF資料の分析と辞書準備に関するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

from ..interfaces.pdf_processor import PDFProcessor, PDFProcessingConfig, PDFContent
from ..interfaces.rag_interface import RAGInterface, KnowledgeItem


class PDFAnalysisService:
    """PDF分析サービス"""
    
    def __init__(
        self, 
        pdf_processor: PDFProcessor,
        rag_interface: Optional[RAGInterface] = None
    ):
        """
        PDF分析サービスを初期化
        
        Args:
            pdf_processor: PDF処理アダプター
            rag_interface: RAGインターフェース（オプション）
        """
        self.pdf_processor = pdf_processor
        self.rag_interface = rag_interface
    
    def analyze_pdf(
        self, 
        pdf_path: str,
        domain: Optional[str] = None,
        config: Optional[PDFProcessingConfig] = None
    ) -> Dict[str, Any]:
        """
        PDFを分析する
        
        Args:
            pdf_path: PDFファイルパス
            domain: 分野
            config: 処理設定
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        if not self.pdf_processor.validate_pdf(pdf_path):
            raise ValueError("Invalid PDF file")
        
        if config is None:
            config = PDFProcessingConfig()
        
        # PDF内容を抽出
        pdf_content = self.pdf_processor.extract_content(pdf_path, config)
        
        # 分析結果を構築
        analysis_result = {
            'pdf_path': pdf_path,
            'content': pdf_content,
            'domain': domain,
            'analysis_timestamp': None
        }
        
        # 文書構造を分析
        structure = self.pdf_processor.analyze_document_structure(pdf_content)
        analysis_result['structure'] = structure
        
        # 重要概念を抽出
        if domain:
            key_concepts = self.pdf_processor.extract_key_concepts(pdf_content, domain)
            analysis_result['key_concepts'] = key_concepts
        
        # 用語辞書を生成
        glossary = self.pdf_processor.generate_glossary_from_pdf(pdf_content, domain)
        analysis_result['glossary'] = glossary
        
        return analysis_result
    
    def generate_glossary_from_pdf(
        self, 
        pdf_path: str,
        domain: Optional[str] = None
    ) -> Dict[str, str]:
        """
        PDFから用語辞書を生成する
        
        Args:
            pdf_path: PDFファイルパス
            domain: 分野
            
        Returns:
            Dict[str, str]: 用語辞書
        """
        pdf_content = self.pdf_processor.extract_content(pdf_path)
        return self.pdf_processor.generate_glossary_from_pdf(pdf_content, domain)
    
    def extract_key_concepts(
        self, 
        pdf_path: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """
        PDFから重要概念を抽出する
        
        Args:
            pdf_path: PDFファイルパス
            domain: 分野
            
        Returns:
            List[str]: 重要概念のリスト
        """
        pdf_content = self.pdf_processor.extract_content(pdf_path)
        return self.pdf_processor.extract_key_concepts(pdf_content, domain)
    
    def prepare_knowledge_base(
        self, 
        pdf_path: str,
        domain: str
    ) -> List[KnowledgeItem]:
        """
        知識ベースを準備する
        
        Args:
            pdf_path: PDFファイルパス
            domain: 分野
            
        Returns:
            List[KnowledgeItem]: 知識アイテムのリスト
        """
        if not self.rag_interface:
            raise ValueError("RAG interface not available")
        
        # PDFを分析
        analysis_result = self.analyze_pdf(pdf_path, domain)
        
        # 知識アイテムを作成
        knowledge_items = []
        
        # テキスト内容から知識アイテムを作成
        text_content = analysis_result['content'].text
        if text_content:
            knowledge_item = KnowledgeItem(
                id=f"pdf_{Path(pdf_path).stem}_text",
                content=text_content,
                domain=domain,
                metadata={
                    'source': 'pdf',
                    'file_path': pdf_path,
                    'type': 'full_text'
                }
            )
            knowledge_items.append(knowledge_item)
        
        # 重要概念から知識アイテムを作成
        key_concepts = analysis_result.get('key_concepts', [])
        for i, concept in enumerate(key_concepts):
            knowledge_item = KnowledgeItem(
                id=f"pdf_{Path(pdf_path).stem}_concept_{i}",
                content=concept,
                domain=domain,
                metadata={
                    'source': 'pdf',
                    'file_path': pdf_path,
                    'type': 'key_concept'
                }
            )
            knowledge_items.append(knowledge_item)
        
        # 用語辞書から知識アイテムを作成
        glossary = analysis_result.get('glossary', {})
        for term, definition in glossary.items():
            knowledge_item = KnowledgeItem(
                id=f"pdf_{Path(pdf_path).stem}_term_{term}",
                content=f"{term}: {definition}",
                domain=domain,
                metadata={
                    'source': 'pdf',
                    'file_path': pdf_path,
                    'type': 'glossary_term',
                    'term': term,
                    'definition': definition
                }
            )
            knowledge_items.append(knowledge_item)
        
        return knowledge_items
    
    def add_pdf_to_knowledge_base(
        self, 
        pdf_path: str,
        domain: str
    ) -> bool:
        """
        PDFを知識ベースに追加する
        
        Args:
            pdf_path: PDFファイルパス
            domain: 分野
            
        Returns:
            bool: 追加の成功/失敗
        """
        if not self.rag_interface:
            raise ValueError("RAG interface not available")
        
        try:
            # 知識ベースを準備
            knowledge_items = self.prepare_knowledge_base(pdf_path, domain)
            
            # 各知識アイテムを追加
            for item in knowledge_items:
                self.rag_interface.add_knowledge(item)
            
            return True
            
        except Exception as e:
            print(f"Error adding PDF to knowledge base: {e}")
            return False
    
    def validate_pdf_for_processing(self, pdf_path: str) -> bool:
        """
        処理用のPDFファイルの妥当性を検証する
        
        Args:
            pdf_path: PDFファイルパス
            
        Returns:
            bool: 妥当性の結果
        """
        if not Path(pdf_path).exists():
            return False
        
        return self.pdf_processor.validate_pdf(pdf_path)
