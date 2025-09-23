"""
音声処理サービス

音声ファイルの処理に関するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any, Iterator
from pathlib import Path
from datetime import datetime

from ..interfaces.audio_processor import AudioProcessor
from ..models.audio_data import AudioData
from utils.audio_utils import validate_audio_file, get_audio_metadata
from utils.streaming_audio_processor import StreamingAudioProcessor, create_streaming_processor
from utils.cloud_audio_manager import CloudAudioManager
from utils.logging import get_logger

logger = get_logger(__name__)


class AudioService:
    """音声処理サービス"""
    
    def __init__(self, 
                 audio_processor: AudioProcessor,
                 cloud_audio_manager: Optional[CloudAudioManager] = None):
        """
        音声処理サービスを初期化
        
        Args:
            audio_processor: 音声処理アダプター
            cloud_audio_manager: クラウド音声マネージャー
        """
        self.audio_processor = audio_processor
        self.cloud_audio_manager = cloud_audio_manager
    
    def process_audio_file(
        self, 
        input_path: str, 
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1,
        filters: Optional[Dict[str, Any]] = None
    ) -> AudioData:
        """
        音声ファイルを処理する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            filters: 適用するフィルタ
            
        Returns:
            AudioData: 処理済み音声データ
            
        Raises:
            FileNotFoundError: 入力ファイルが存在しない場合
            ValueError: 音声ファイルが無効な場合
            RuntimeError: 音声処理に失敗した場合
        """
        try:
            # 入力ファイルの存在チェック
            if not Path(input_path).exists():
                raise FileNotFoundError(f"Input audio file not found: {input_path}")
            
            # 入力ファイルの妥当性チェック
            is_valid, error_msg = validate_audio_file(input_path)
            if not is_valid:
                raise ValueError(f"Invalid input audio file: {error_msg}")
            
            logger.info(f"Processing audio file: {input_path}")
            
            # 音声抽出
            audio_data = self.audio_processor.extract_audio(
                input_path, output_path, sample_rate, channels
            )
            
            # 前処理
            if filters:
                logger.info(f"Applying audio filters: {filters}")
                audio_data = self.audio_processor.preprocess_audio(audio_data, filters)
            
            # 妥当性検証
            if not self.audio_processor.validate_audio(audio_data):
                raise ValueError("Audio processing resulted in invalid audio data")
            
            logger.info(f"Audio processing completed successfully: {output_path}")
            return audio_data
            
        except FileNotFoundError:
            logger.error(f"File not found: {input_path}")
            raise
        except ValueError as e:
            logger.error(f"Invalid audio file: {e}")
            raise
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise RuntimeError(f"Failed to process audio file: {str(e)}")
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        音声ファイルの妥当性を検証する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 妥当性の結果
        """
        try:
            is_valid, _ = validate_audio_file(file_path)
            return is_valid
        except Exception as e:
            logger.error(f"Audio file validation failed: {e}")
            return False
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        音声ファイルの情報を取得する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            Dict[str, Any]: 音声情報
        """
        if not self.validate_audio_file(file_path):
            raise ValueError("Invalid audio file")
        
        # 音声データを作成
        audio_data = AudioData(
            file_path=file_path,
            file_size=Path(file_path).stat().st_size,
            duration=0,
            sample_rate=0,
            channels=0,
            bit_depth=0,
            format=Path(file_path).suffix,
            created_at=None,
            metadata={}
        )
        
        return self.audio_processor.get_audio_info(audio_data)
    
    def optimize_for_transcription(
        self, 
        input_path: str, 
        output_path: str
    ) -> AudioData:
        """
        文字起こし用に音声を最適化する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            
        Returns:
            AudioData: 最適化済み音声データ
        """
        # 文字起こし用の最適化設定
        filters = {
            'highpass': 80,
            'lowpass': 8000,
            'volume': 1.2,
            'noise_reduction': True
        }
        
        return self.process_audio_file(
            input_path, 
            output_path, 
            sample_rate=16000, 
            channels=1, 
            filters=filters
        )
    
    def process_large_audio_file(
        self, 
        input_path: str, 
        output_dir: str,
        max_memory_mb: int = 1024,
        sample_rate: int = 16000,
        channels: int = 1,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        大容量音声ファイルをストリーミング処理する
        
        Args:
            input_path: 入力ファイルパス
            output_dir: 出力ディレクトリ
            max_memory_mb: 最大メモリ使用量（MB）
            sample_rate: サンプルレート
            channels: チャンネル数
            filters: 適用するフィルタ
            
        Returns:
            Dict[str, Any]: 処理結果（チャンク情報を含む）
            
        Raises:
            FileNotFoundError: 入力ファイルが存在しない場合
            ValueError: 音声ファイルが無効な場合
            RuntimeError: 音声処理に失敗した場合
        """
        try:
            # 入力ファイルの存在チェック
            if not Path(input_path).exists():
                raise FileNotFoundError(f"Input audio file not found: {input_path}")
            
            # 入力ファイルの妥当性チェック
            is_valid, error_msg = validate_audio_file(input_path)
            if not is_valid:
                raise ValueError(f"Invalid input audio file: {error_msg}")
            
            # 音声メタデータを取得
            metadata = get_audio_metadata(input_path)
            file_duration = metadata['duration']
            
            logger.info(f"Processing large audio file: {input_path} (duration: {file_duration:.2f}s)")
            
            # ストリーミングプロセッサを作成
            processor = create_streaming_processor(
                file_duration=file_duration,
                max_memory_mb=max_memory_mb,
                temp_dir=output_dir
            )
            
            # 出力ディレクトリを作成
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # チャンク処理結果を保存
            chunk_results = []
            
            with processor:
                # 各チャンクを処理
                for chunk_info in processor.split_audio_file(input_path):
                    logger.info(f"Processing chunk {chunk_info['chunk_index'] + 1}/{chunk_info['total_chunks']}")
                    
                    # チャンクファイル名を生成
                    chunk_filename = f"chunk_{chunk_info['chunk_index']:04d}.wav"
                    chunk_output_path = Path(output_dir) / chunk_filename
                    
                    # チャンクを処理
                    chunk_audio_data = self.audio_processor.extract_audio(
                        chunk_info['chunk_path'],
                        str(chunk_output_path),
                        sample_rate,
                        channels
                    )
                    
                    # 前処理を適用
                    if filters:
                        chunk_audio_data = self.audio_processor.preprocess_audio(
                            chunk_audio_data, 
                            filters
                        )
                    
                    # チャンク結果を保存
                    chunk_result = {
                        'chunk_index': chunk_info['chunk_index'],
                        'chunk_path': str(chunk_output_path),
                        'start_time': chunk_info['start_time'],
                        'end_time': chunk_info['end_time'],
                        'duration': chunk_info['duration'],
                        'audio_data': chunk_audio_data
                    }
                    chunk_results.append(chunk_result)
            
            # 処理結果をまとめる
            result = {
                'input_path': input_path,
                'output_dir': output_dir,
                'total_duration': file_duration,
                'total_chunks': len(chunk_results),
                'chunks': chunk_results,
                'metadata': metadata
            }
            
            logger.info(f"Large audio file processing completed: {len(chunk_results)} chunks")
            return result
            
        except FileNotFoundError:
            logger.error(f"File not found: {input_path}")
            raise
        except ValueError as e:
            logger.error(f"Invalid audio file: {e}")
            raise
        except Exception as e:
            logger.error(f"Large audio file processing failed: {e}")
            raise RuntimeError(f"Failed to process large audio file: {str(e)}")
    
    def merge_audio_chunks(
        self, 
        chunk_paths: list, 
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> AudioData:
        """
        音声チャンクをマージする
        
        Args:
            chunk_paths: チャンクファイルパスのリスト
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            
        Returns:
            AudioData: マージされた音声データ
        """
        try:
            import ffmpeg
            
            # 出力ディレクトリを作成
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # チャンクファイルを連結
            inputs = [ffmpeg.input(path) for path in chunk_paths]
            
            # 音声を連結
            (
                ffmpeg
                .concat(*inputs, v=0, a=1)  # 音声のみ連結
                .output(
                    output_path,
                    acodec='pcm_s16le',
                    ar=sample_rate,
                    ac=channels
                )
                .run(quiet=True, overwrite_output=True)
            )
            
            # マージされた音声データを作成
            output_metadata = get_audio_metadata(output_path)
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
            
            logger.info(f"Audio chunks merged: {output_path}")
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to merge audio chunks: {e}")
            raise
    
    def process_audio_with_cloud_storage(
        self, 
        input_path: str,
        bucket_name: str,
        max_memory_mb: int = 1024,
        sample_rate: int = 16000,
        channels: int = 1,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        音声ファイルをクラウドストレージで管理しながら処理
        
        Args:
            input_path: 入力ファイルパス
            bucket_name: GCSバケット名
            max_memory_mb: 最大メモリ使用量（MB）
            sample_rate: サンプルレート
            channels: チャンネル数
            filters: 適用するフィルタ
            
        Returns:
            Dict[str, Any]: 処理結果（セッション情報を含む）
        """
        if not self.cloud_audio_manager:
            raise ValueError("Cloud audio manager not initialized")
        
        try:
            # 入力ファイルの妥当性チェック
            is_valid, error_msg = validate_audio_file(input_path)
            if not is_valid:
                raise ValueError(f"Invalid input audio file: {error_msg}")
            
            # 音声メタデータを取得
            metadata = get_audio_metadata(input_path)
            file_duration = metadata['duration']
            
            logger.info(f"Processing audio with cloud storage: {input_path} (duration: {file_duration:.2f}s)")
            
            # 音声セッションを作成
            session_id = self.cloud_audio_manager.create_audio_session(
                original_filename=Path(input_path).name,
                duration=file_duration,
                metadata=metadata
            )
            
            # ストリーミングプロセッサを作成
            processor = create_streaming_processor(
                file_duration=file_duration,
                max_memory_mb=max_memory_mb
            )
            
            # チャンク処理結果を保存
            chunk_results = []
            
            with processor:
                # 各チャンクを処理
                for chunk_info in processor.split_audio_file(input_path):
                    logger.info(f"Processing chunk {chunk_info['chunk_index'] + 1}/{chunk_info['total_chunks']}")
                    
                    # チャンクを一時的に処理
                    temp_chunk_path = chunk_info['chunk_path']
                    
                    # 音声抽出と前処理
                    chunk_audio_data = self.audio_processor.extract_audio(
                        temp_chunk_path,
                        temp_chunk_path,  # 同じファイルを上書き
                        sample_rate,
                        channels
                    )
                    
                    # 前処理を適用
                    if filters:
                        chunk_audio_data = self.audio_processor.preprocess_audio(
                            chunk_audio_data, 
                            filters
                        )
                    
                    # チャンクをクラウドストレージにアップロード
                    cloud_chunk_info = self.cloud_audio_manager.upload_chunk(
                        session_id=session_id,
                        chunk_index=chunk_info['chunk_index'],
                        chunk_path=temp_chunk_path,
                        start_time=chunk_info['start_time'],
                        end_time=chunk_info['end_time']
                    )
                    
                    chunk_results.append(cloud_chunk_info)
            
            # セッションステータスを完了に更新
            self.cloud_audio_manager.update_session_status(
                session_id=session_id,
                status='completed',
                additional_info={
                    'total_chunks': len(chunk_results),
                    'processing_completed_at': datetime.utcnow().isoformat()
                }
            )
            
            # 処理結果をまとめる
            result = {
                'session_id': session_id,
                'input_path': input_path,
                'total_duration': file_duration,
                'total_chunks': len(chunk_results),
                'chunks': chunk_results,
                'metadata': metadata,
                'cloud_storage': {
                    'bucket_name': bucket_name,
                    'base_path': f"audio_chunks/{session_id}"
                }
            }
            
            logger.info(f"Audio processing with cloud storage completed: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process audio with cloud storage: {e}")
            # エラー時はセッションステータスを失敗に更新
            if 'session_id' in locals():
                try:
                    self.cloud_audio_manager.update_session_status(
                        session_id=session_id,
                        status='failed',
                        additional_info={'error': str(e)}
                    )
                except Exception as update_error:
                    logger.error(f"Failed to update session status: {update_error}")
            raise
    
    def get_audio_session(self, session_id: str) -> Dict[str, Any]:
        """
        音声セッション情報を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Dict[str, Any]: セッション情報
        """
        if not self.cloud_audio_manager:
            raise ValueError("Cloud audio manager not initialized")
        
        return self.cloud_audio_manager.get_session_info(session_id)
    
    def stream_audio_chunks(self, session_id: str) -> Iterator[Dict[str, Any]]:
        """
        音声セッションのチャンクをストリーミング取得
        
        Args:
            session_id: セッションID
            
        Yields:
            Dict[str, Any]: チャンク情報（ローカルパスを含む）
        """
        if not self.cloud_audio_manager:
            raise ValueError("Cloud audio manager not initialized")
        
        return self.cloud_audio_manager.stream_chunks(session_id)
    
    def merge_cloud_audio_chunks(self, 
                                session_id: str, 
                                output_path: str,
                                sample_rate: int = 16000,
                                channels: int = 1) -> Dict[str, Any]:
        """
        クラウドストレージの音声チャンクをマージ
        
        Args:
            session_id: セッションID
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            
        Returns:
            Dict[str, Any]: マージ結果
        """
        if not self.cloud_audio_manager:
            raise ValueError("Cloud audio manager not initialized")
        
        return self.cloud_audio_manager.merge_chunks(
            session_id=session_id,
            output_path=output_path,
            sample_rate=sample_rate,
            channels=channels
        )
