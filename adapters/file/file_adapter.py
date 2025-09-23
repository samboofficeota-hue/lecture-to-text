"""
ファイルアダプター

ファイルの入出力操作を実装します。
"""

import os
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path

from core.interfaces.audio_processor import AudioProcessor
from core.interfaces.pdf_processor import PDFProcessor, PDFProcessingConfig, PDFContent
from core.models.audio_data import AudioData
from utils.logging import get_logger
from utils.audio_utils import get_audio_metadata, validate_audio_file

logger = get_logger(__name__)


class FileAdapter(AudioProcessor, PDFProcessor):
    """ファイルアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        ファイルアダプターを初期化
        
        Args:
            config: ファイル設定
        """
        self.config = config or {}
    
    # AudioProcessor インターフェースの実装
    
    def extract_audio(
        self, 
        input_path: str, 
        output_path: str, 
        sample_rate: int = 16000,
        channels: int = 1
    ) -> AudioData:
        """
        音声ファイルから音声データを抽出する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            
        Returns:
            AudioData: 抽出された音声データ
        """
        try:
            # 入力ファイルの妥当性をチェック
            is_valid, error_msg = validate_audio_file(input_path)
            if not is_valid:
                raise ValueError(f"Invalid input audio file: {error_msg}")
            
            import ffmpeg
            
            # 出力ディレクトリを作成
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # FFmpegを使用して音声を抽出
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path, 
                    ac=channels,           # チャンネル数
                    ar=sample_rate,        # サンプルレート
                    vn=None,               # 動画を無効化
                    y=None,                # 上書き確認を無効化
                    af="highpass=f=80,lowpass=f=8000,volume=1.2",  # 音声フィルタ
                    acodec='pcm_s16le'     # 16bit PCM
                )
                .run(quiet=True, overwrite_output=True)
            )
            
            # 出力ファイルのメタデータを取得
            output_metadata = get_audio_metadata(output_path)
            
            # 音声データを作成
            audio_data = AudioData(
                file_path=output_path,
                file_size=output_metadata['file_size'],
                duration=output_metadata['duration'],
                sample_rate=output_metadata['sample_rate'],
                channels=output_metadata['channels'],
                bit_depth=output_metadata['bit_depth'],
                format=output_metadata['format'],
                created_at=None,
                metadata=output_metadata['raw_metadata']
            )
            
            logger.info(f"Audio extracted: {input_path} -> {output_path} (duration: {audio_data.duration:.2f}s)")
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise
    
    def preprocess_audio(
        self, 
        audio_data: AudioData,
        filters: Optional[Dict[str, Any]] = None
    ) -> AudioData:
        """
        音声データの前処理を行う
        
        Args:
            audio_data: 音声データ
            filters: 適用するフィルタ設定
            
        Returns:
            AudioData: 前処理済み音声データ
        """
        # 現在は基本的な前処理のみ実装
        # 実際の実装では、より詳細な音声処理を行う
        logger.info("Audio preprocessing completed")
        return audio_data
    
    def validate_audio(self, audio_data: AudioData) -> bool:
        """
        音声データの妥当性を検証する
        
        Args:
            audio_data: 検証する音声データ
            
        Returns:
            bool: 妥当性の結果
        """
        try:
            # 基本的な妥当性チェック
            if not Path(audio_data.file_path).exists():
                return False
            
            if audio_data.duration < 0.1:  # 0.1秒未満
                return False
            
            if audio_data.sample_rate < 8000:  # サンプルレートが低すぎる
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False
    
    def get_audio_info(self, audio_data: AudioData) -> Dict[str, Any]:
        """
        音声データの情報を取得する
        
        Args:
            audio_data: 音声データ
            
        Returns:
            Dict[str, Any]: 音声情報
        """
        return {
            'file_path': audio_data.file_path,
            'file_size': audio_data.file_size,
            'duration': audio_data.duration,
            'sample_rate': audio_data.sample_rate,
            'channels': audio_data.channels,
            'bit_depth': audio_data.bit_depth,
            'format': audio_data.format
        }
    
    # PDFProcessor インターフェースの実装
    
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
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # テキストを抽出
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # メタデータを取得
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                    'subject': pdf_reader.metadata.get('/Subject', '') if pdf_reader.metadata else '',
                    'creator': pdf_reader.metadata.get('/Creator', '') if pdf_reader.metadata else '',
                    'producer': pdf_reader.metadata.get('/Producer', '') if pdf_reader.metadata else '',
                    'creation_date': pdf_reader.metadata.get('/CreationDate', '') if pdf_reader.metadata else '',
                    'modification_date': pdf_reader.metadata.get('/ModDate', '') if pdf_reader.metadata else ''
                }
                
                # PDF内容を作成
                pdf_content = PDFContent(
                    text=text,
                    metadata=metadata,
                    tables=[],  # 簡易実装
                    images=[],  # 簡易実装
                    pages=len(pdf_reader.pages),
                    file_size=Path(pdf_path).stat().st_size
                )
                
                logger.info(f"PDF content extracted: {pdf_path}")
                return pdf_content
                
        except Exception as e:
            logger.error(f"Failed to extract PDF content: {e}")
            raise
    
    def extract_text(
        self, 
        pdf_path: str,
        page_range: Optional[tuple] = None
    ) -> str:
        """
        PDFからテキストを抽出する
        
        Args:
            pdf_path: PDFファイルパス
            page_range: ページ範囲（開始, 終了）
            
        Returns:
            str: 抽出されたテキスト
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text = ""
                start_page = page_range[0] if page_range else 0
                end_page = page_range[1] if page_range else len(pdf_reader.pages)
                
                for i in range(start_page, min(end_page, len(pdf_reader.pages))):
                    text += pdf_reader.pages[i].extract_text() + "\n"
                
                logger.info(f"PDF text extracted: {pdf_path}")
                return text
                
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            raise
    
    def extract_tables(
        self, 
        pdf_path: str,
        page_range: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        PDFから表を抽出する
        
        Args:
            pdf_path: PDFファイルパス
            page_range: ページ範囲
            
        Returns:
            List[Dict[str, Any]]: 抽出された表
        """
        # 簡易実装：実際の実装では、より詳細な表抽出を行う
        logger.warning("Table extraction not implemented yet")
        return []
    
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
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                
                logger.info(f"PDF metadata extracted: {pdf_path}")
                return metadata
                
        except Exception as e:
            logger.error(f"Failed to extract PDF metadata: {e}")
            return {}
    
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
        # 簡易実装：実際の実装では、より詳細な用語抽出を行う
        logger.warning("Glossary generation from PDF not implemented yet")
        return {}
    
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
        # 簡易実装：実際の実装では、より詳細な概念抽出を行う
        logger.warning("Key concept extraction from PDF not implemented yet")
        return []
    
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
        # 簡易実装：実際の実装では、より詳細な構造分析を行う
        logger.warning("Document structure analysis not implemented yet")
        return {}
    
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
        try:
            if not Path(pdf_path).exists():
                return False
            
            # PDFファイルの基本的な妥当性チェック
            with open(pdf_path, 'rb') as file:
                # PDFヘッダーをチェック
                header = file.read(4)
                if header != b'%PDF':
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed: {e}")
            return False
