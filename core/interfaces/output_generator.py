"""
出力生成インターフェース

処理済みテキストから各種出力形式を生成する抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..models.processing_result import ProcessingResult


class OutputFormat(Enum):
    """出力形式"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


@dataclass
class OutputConfig:
    """出力設定"""
    format: OutputFormat = OutputFormat.MARKDOWN
    title: str = "講義録"
    include_timestamps: bool = True
    include_glossary: bool = True
    include_summary: bool = True
    include_questions: bool = True
    template_path: Optional[str] = None
    custom_styles: Optional[Dict[str, Any]] = None


class OutputGenerator(ABC):
    """出力生成の抽象インターフェース"""
    
    @abstractmethod
    def generate_output(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        処理結果から出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: 生成された出力
        """
        pass
    
    @abstractmethod
    def generate_markdown(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        Markdown形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: Markdown形式の出力
        """
        pass
    
    @abstractmethod
    def generate_html(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        HTML形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: HTML形式の出力
        """
        pass
    
    @abstractmethod
    def generate_pdf(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> bytes:
        """
        PDF形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            bytes: PDF形式の出力
        """
        pass
    
    @abstractmethod
    def generate_summary(
        self, 
        processing_result: ProcessingResult,
        max_length: int = 1000
    ) -> str:
        """
        サマリーを生成する
        
        Args:
            processing_result: 処理結果
            max_length: 最大文字数
            
        Returns:
            str: サマリー
        """
        pass
    
    @abstractmethod
    def generate_glossary(
        self, 
        processing_result: ProcessingResult
    ) -> List[Dict[str, str]]:
        """
        用語集を生成する
        
        Args:
            processing_result: 処理結果
            
        Returns:
            List[Dict[str, str]]: 用語集
        """
        pass
    
    @abstractmethod
    def generate_questions(
        self, 
        processing_result: ProcessingResult,
        num_questions: int = 5
    ) -> List[str]:
        """
        確認問題を生成する
        
        Args:
            processing_result: 処理結果
            num_questions: 問題数
            
        Returns:
            List[str]: 確認問題
        """
        pass
