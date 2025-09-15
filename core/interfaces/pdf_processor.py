"""
PDF処理インターフェース

PDF資料からテキストやメタデータを抽出し、辞書準備に活用する抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from ..models.processing_result import ProcessingResult


@dataclass
class PDFProcessingConfig:
    """PDF処理設定"""
    extract_text: bool = True
    extract_images: bool = False
    extract_tables: bool = True
    extract_metadata: bool = True
    language: str = "ja"
    ocr_enabled: bool = True
    table_extraction_method: str = "auto"


@dataclass
class PDFContent:
    """PDF内容"""
    text: str
    metadata: Dict[str, Any]
    tables: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    pages: int
    file_size: int


class PDFProcessor(ABC):
    """PDF処理の抽象インターフェース"""
    
    @abstractmethod
    def extract_content(
        self, 
        pdf_path: str,
        config: Optional[PDFProcessingConfig] = None
    ) -> PDFContent:
        """
        PDFから内容を抽出する
        
        Args:
            pdf_path: PDFファイルパス
            config: 処理設定
            
        Returns:
            PDFContent: 抽出された内容
        """
        pass
    
    @abstractmethod
    def extract_text(
        self, 
        pdf_path: str,
        page_range: Optional[Tuple[int, int]] = None
    ) -> str:
        """
        PDFからテキストを抽出する
        
        Args:
            pdf_path: PDFファイルパス
            page_range: ページ範囲（開始, 終了）
            
        Returns:
            str: 抽出されたテキスト
        """
        pass
    
    @abstractmethod
    def extract_tables(
        self, 
        pdf_path: str,
        page_range: Optional[Tuple[int, int]] = None
    ) -> List[Dict[str, Any]]:
        """
        PDFから表を抽出する
        
        Args:
            pdf_path: PDFファイルパス
            page_range: ページ範囲
            
        Returns:
            List[Dict[str, Any]]: 抽出された表
        """
        pass
    
    @abstractmethod
    def extract_metadata(
        self, 
        pdf_path: str
    ) -> Dict[str, Any]:
        """
        PDFからメタデータを抽出する
        
        Args:
            pdf_path: PDFファイルパス
            
        Returns:
            Dict[str, Any]: メタデータ
        """
        pass
    
    @abstractmethod
    def generate_glossary_from_pdf(
        self, 
        pdf_content: PDFContent,
        domain: Optional[str] = None
    ) -> Dict[str, str]:
        """
        PDF内容から用語辞書を生成する
        
        Args:
            pdf_content: PDF内容
            domain: 分野
            
        Returns:
            Dict[str, str]: 用語辞書
        """
        pass
    
    @abstractmethod
    def extract_key_concepts(
        self, 
        pdf_content: PDFContent,
        domain: Optional[str] = None
    ) -> List[str]:
        """
        PDF内容から重要概念を抽出する
        
        Args:
            pdf_content: PDF内容
            domain: 分野
            
        Returns:
            List[str]: 重要概念のリスト
        """
        pass
    
    @abstractmethod
    def analyze_document_structure(
        self, 
        pdf_content: PDFContent
    ) -> Dict[str, Any]:
        """
        文書構造を分析する
        
        Args:
            pdf_content: PDF内容
            
        Returns:
            Dict[str, Any]: 文書構造分析結果
        """
        pass
    
    @abstractmethod
    def validate_pdf(
        self, 
        pdf_path: str
    ) -> bool:
        """
        PDFファイルの妥当性を検証する
        
        Args:
            pdf_path: PDFファイルパス
            
        Returns:
            bool: 妥当性の結果
        """
        pass
