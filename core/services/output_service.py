"""
出力生成サービス

処理済みテキストから各種出力形式を生成するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from ..interfaces.output_generator import OutputGenerator, OutputConfig, OutputFormat
from ..models.processing_result import ProcessingResult


class OutputService:
    """出力生成サービス"""
    
    def __init__(self, output_generator: OutputGenerator):
        """
        出力生成サービスを初期化
        
        Args:
            output_generator: 出力生成アダプター
        """
        self.output_generator = output_generator
    
    def generate_lecture_output(
        self, 
        processing_result: ProcessingResult,
        title: str = "講義録",
        format: OutputFormat = OutputFormat.MARKDOWN,
        include_timestamps: bool = True,
        include_glossary: bool = True,
        include_summary: bool = True,
        include_questions: bool = True
    ) -> str:
        """
        講義録出力を生成する
        
        Args:
            processing_result: 処理結果
            title: タイトル
            format: 出力形式
            include_timestamps: タイムスタンプを含むか
            include_glossary: 用語集を含むか
            include_summary: サマリーを含むか
            include_questions: 確認問題を含むか
            
        Returns:
            str: 生成された出力
        """
        config = OutputConfig(
            format=format,
            title=title,
            include_timestamps=include_timestamps,
            include_glossary=include_glossary,
            include_summary=include_summary,
            include_questions=include_questions
        )
        
        return self.output_generator.generate_output(processing_result, config)
    
    def generate_markdown_output(
        self, 
        processing_result: ProcessingResult,
        title: str = "講義録"
    ) -> str:
        """
        Markdown形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            title: タイトル
            
        Returns:
            str: Markdown形式の出力
        """
        config = OutputConfig(
            format=OutputFormat.MARKDOWN,
            title=title
        )
        
        return self.output_generator.generate_markdown(processing_result, config)
    
    def generate_html_output(
        self, 
        processing_result: ProcessingResult,
        title: str = "講義録"
    ) -> str:
        """
        HTML形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            title: タイトル
            
        Returns:
            str: HTML形式の出力
        """
        config = OutputConfig(
            format=OutputFormat.HTML,
            title=title
        )
        
        return self.output_generator.generate_html(processing_result, config)
    
    def generate_pdf_output(
        self, 
        processing_result: ProcessingResult,
        title: str = "講義録"
    ) -> bytes:
        """
        PDF形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            title: タイトル
            
        Returns:
            bytes: PDF形式の出力
        """
        config = OutputConfig(
            format=OutputFormat.PDF,
            title=title
        )
        
        return self.output_generator.generate_pdf(processing_result, config)
    
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
        return self.output_generator.generate_summary(processing_result, max_length)
    
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
        return self.output_generator.generate_glossary(processing_result)
    
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
        return self.output_generator.generate_questions(processing_result, num_questions)
    
    def save_output(
        self, 
        output: str,
        output_path: str,
        format: OutputFormat = OutputFormat.MARKDOWN
    ) -> bool:
        """
        出力をファイルに保存する
        
        Args:
            output: 出力内容
            output_path: 保存先パス
            format: 出力形式
            
        Returns:
            bool: 保存の成功/失敗
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 形式に応じてファイル拡張子を設定
            if not output_file.suffix:
                extensions = {
                    OutputFormat.MARKDOWN: '.md',
                    OutputFormat.HTML: '.html',
                    OutputFormat.PDF: '.pdf',
                    OutputFormat.DOCX: '.docx',
                    OutputFormat.TXT: '.txt'
                }
                output_file = output_file.with_suffix(extensions[format])
            
            # ファイルに書き込み
            if format == OutputFormat.PDF:
                # PDFの場合はバイナリモード
                with open(output_file, 'wb') as f:
                    f.write(output.encode('utf-8'))
            else:
                # その他の場合はテキストモード
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)
            
            return True
            
        except Exception as e:
            print(f"Error saving output: {e}")
            return False
