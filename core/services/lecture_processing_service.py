"""
講義処理サービス

講義録作成の全体的なワークフローを管理するメインサービスです。
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import time

from ..interfaces.audio_processor import AudioProcessor
from ..interfaces.transcriber import Transcriber, TranscriptionConfig
from ..interfaces.text_processor import TextProcessor, TextProcessingConfig
from ..interfaces.output_generator import OutputGenerator, OutputConfig, OutputFormat
from ..interfaces.rag_interface import RAGInterface, RAGConfig
from ..interfaces.pdf_processor import PDFProcessor, PDFProcessingConfig

from ..models.audio_data import AudioData
from ..models.transcription_data import TranscriptionData
from ..models.processing_result import ProcessingResult, ProcessingStatus
from ..models.lecture_record import LectureRecord, LectureMetadata, LectureStatus


class LectureProcessingService:
    """講義処理サービス"""
    
    def __init__(
        self,
        audio_processor: AudioProcessor,
        transcriber: Transcriber,
        text_processor: TextProcessor,
        output_generator: OutputGenerator,
        rag_interface: Optional[RAGInterface] = None,
        pdf_processor: Optional[PDFProcessor] = None
    ):
        """
        講義処理サービスを初期化
        
        Args:
            audio_processor: 音声処理アダプター
            transcriber: 文字起こしアダプター
            text_processor: テキスト処理アダプター
            output_generator: 出力生成アダプター
            rag_interface: RAGインターフェース（オプション）
            pdf_processor: PDF処理アダプター（オプション）
        """
        self.audio_processor = audio_processor
        self.transcriber = transcriber
        self.text_processor = text_processor
        self.output_generator = output_generator
        self.rag_interface = rag_interface
        self.pdf_processor = pdf_processor
    
    def process_lecture(
        self,
        audio_file_path: str,
        pdf_file_path: Optional[str] = None,
        title: str = "講義録",
        domain: str = "会計・財務",
        output_dir: str = "./output",
        transcription_config: Optional[TranscriptionConfig] = None,
        text_processing_config: Optional[TextProcessingConfig] = None,
        output_config: Optional[OutputConfig] = None,
        use_rag: bool = True
    ) -> LectureRecord:
        """
        講義を処理して講義録を作成する
        
        Args:
            audio_file_path: 音声ファイルパス
            pdf_file_path: PDFファイルパス（オプション）
            title: 講義タイトル
            domain: 分野
            output_dir: 出力ディレクトリ
            transcription_config: 文字起こし設定
            text_processing_config: テキスト処理設定
            output_config: 出力設定
            use_rag: RAGを使用するか
            
        Returns:
            LectureRecord: 講義記録
        """
        # 出力ディレクトリを作成
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 講義記録を作成
        lecture_id = f"lecture_{int(time.time())}"
        lecture_metadata = LectureMetadata(
            title=title,
            instructor="Unknown",  # 後で設定可能
            date=None,  # 後で設定可能
            duration=0.0,  # 後で更新
            domain=domain
        )
        
        lecture_record = LectureRecord(
            id=lecture_id,
            metadata=lecture_metadata,
            audio_file_path=audio_file_path,
            pdf_file_path=pdf_file_path,
            status=LectureStatus.PROCESSING
        )
        
        try:
            # 1. 音声処理
            lecture_record.add_processing_log("audio_processing", "started")
            audio_data = self._process_audio(audio_file_path, output_path)
            lecture_record.metadata.duration = audio_data.duration
            lecture_record.add_processing_log("audio_processing", "completed", {
                "duration": audio_data.duration,
                "sample_rate": audio_data.sample_rate
            })
            
            # 2. PDF処理（オプション）
            if pdf_file_path and self.pdf_processor:
                lecture_record.add_processing_log("pdf_processing", "started")
                self._process_pdf(pdf_file_path, domain, output_path)
                lecture_record.add_processing_log("pdf_processing", "completed")
            
            # 3. 文字起こし
            lecture_record.add_processing_log("transcription", "started")
            transcription_data = self._transcribe_audio(
                audio_data, transcription_config, domain
            )
            raw_transcript_path = output_path / "transcript.raw.txt"
            raw_transcript_path.write_text(transcription_data.full_text, encoding="utf-8")
            lecture_record.raw_transcript_path = str(raw_transcript_path)
            lecture_record.add_processing_log("transcription", "completed", {
                "word_count": transcription_data.word_count,
                "segment_count": transcription_data.segment_count
            })
            
            # 4. テキスト処理
            lecture_record.add_processing_log("text_processing", "started")
            processing_result = self._process_text(
                transcription_data, text_processing_config, domain, use_rag
            )
            processed_transcript_path = output_path / "transcript.processed.txt"
            processed_transcript_path.write_text(processing_result.processed_text, encoding="utf-8")
            lecture_record.processed_transcript_path = str(processed_transcript_path)
            lecture_record.add_processing_log("text_processing", "completed", {
                "quality_score": processing_result.get_quality_score()
            })
            
            # 5. 出力生成
            lecture_record.add_processing_log("output_generation", "started")
            final_output = self._generate_output(
                processing_result, output_config, title, output_path
            )
            final_transcript_path = output_path / "final_transcript.md"
            final_transcript_path.write_text(final_output, encoding="utf-8")
            lecture_record.final_transcript_path = str(final_transcript_path)
            lecture_record.add_processing_log("output_generation", "completed")
            
            # 6. 完了
            lecture_record.update_status(LectureStatus.COMPLETED)
            lecture_record.add_processing_log("lecture_processing", "completed")
            
            return lecture_record
            
        except Exception as e:
            # エラー処理
            lecture_record.update_status(LectureStatus.DRAFT)
            lecture_record.add_processing_log("lecture_processing", "failed", {
                "error": str(e)
            })
            raise
    
    def _process_audio(self, audio_file_path: str, output_path: Path) -> AudioData:
        """音声処理を実行"""
        # 音声抽出用の出力パス
        wav_path = output_path / "audio.wav"
        
        # 音声抽出
        audio_data = self.audio_processor.extract_audio(
            audio_file_path, 
            str(wav_path), 
            sample_rate=16000, 
            channels=1
        )
        
        # 前処理（文字起こし用に最適化）
        filters = {
            'highpass': 80,
            'lowpass': 8000,
            'volume': 1.2,
            'noise_reduction': True
        }
        audio_data = self.audio_processor.preprocess_audio(audio_data, filters)
        
        return audio_data
    
    def _process_pdf(self, pdf_file_path: str, domain: str, output_path: Path) -> None:
        """PDF処理を実行"""
        if not self.pdf_processor:
            return
        
        # PDF内容を抽出
        pdf_content = self.pdf_processor.extract_content(pdf_file_path)
        
        # 用語辞書を生成
        glossary = self.pdf_processor.generate_glossary_from_pdf(pdf_content, domain)
        
        # 辞書を保存
        glossary_path = output_path / "glossary_from_pdf.csv"
        import csv
        with open(glossary_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['term', 'normalized'])
            for term, normalized in glossary.items():
                writer.writerow([term, normalized])
        
        # RAGに知識を追加
        if self.rag_interface:
            self._add_pdf_to_rag(pdf_content, domain)
    
    def _transcribe_audio(
        self, 
        audio_data: AudioData, 
        config: Optional[TranscriptionConfig], 
        domain: str
    ) -> TranscriptionData:
        """文字起こしを実行"""
        if config is None:
            config = TranscriptionConfig()
            # 分野に応じた最適化
            if domain == "会計・財務":
                config.initial_prompt = "これは会計・財務の講義です。専門用語が多く含まれています。"
            elif domain == "技術・工学":
                config.initial_prompt = "これは技術・工学の講義です。専門用語が多く含まれています。"
            elif domain == "経済学":
                config.initial_prompt = "これは経済学の講義です。専門用語が多く含まれています。"
        
        return self.transcriber.transcribe_with_timestamps(audio_data, config)
    
    def _process_text(
        self, 
        transcription_data: TranscriptionData,
        config: Optional[TextProcessingConfig],
        domain: str,
        use_rag: bool
    ) -> ProcessingResult:
        """テキスト処理を実行"""
        if config is None:
            config = TextProcessingConfig(domain=domain)
        
        # 基本的なテキスト処理
        processing_result = self.text_processor.process_transcription(
            transcription_data, config
        )
        
        # RAG処理（オプション）
        if use_rag and self.rag_interface:
            rag_config = RAGConfig(domain=domain)
            enhanced_text = self.rag_interface.process_with_rag(
                processing_result.processed_text, rag_config
            )
            processing_result.enhanced_text = enhanced_text
            processing_result.add_metadata('rag_processed', True)
        
        return processing_result
    
    def _generate_output(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig],
        title: str,
        output_path: Path
    ) -> str:
        """出力を生成"""
        if config is None:
            config = OutputConfig(
                format=OutputFormat.MARKDOWN,
                title=title,
                include_timestamps=True,
                include_glossary=True,
                include_summary=True,
                include_questions=True
            )
        
        return self.output_generator.generate_output(processing_result, config)
    
    def _add_pdf_to_rag(self, pdf_content, domain: str) -> None:
        """PDF内容をRAGに追加"""
        if not self.rag_interface:
            return
        
        # 簡易実装：PDF内容を知識として追加
        # 実際の実装では、より詳細な知識抽出を行う
        pass
