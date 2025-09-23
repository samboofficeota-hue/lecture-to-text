"""
ストリーミング音声処理ユーティリティ

大容量音声ファイルをメモリ効率的に処理するためのストリーミング機能を提供します。
"""

import os
import tempfile
import gc
from typing import Iterator, Dict, Any, Optional, Tuple
from pathlib import Path
import subprocess
import psutil

from utils.logging import get_logger
from utils.audio_utils import get_audio_metadata, validate_audio_file

logger = get_logger(__name__)


class StreamingAudioProcessor:
    """ストリーミング音声処理クラス"""
    
    def __init__(self, 
                 chunk_duration: int = 300,  # 5分チャンク
                 max_memory_mb: int = 1024,  # 最大メモリ使用量（MB）
                 temp_dir: Optional[str] = None):
        """
        ストリーミング音声プロセッサを初期化
        
        Args:
            chunk_duration: チャンクの長さ（秒）
            max_memory_mb: 最大メモリ使用量（MB）
            temp_dir: 一時ディレクトリ
        """
        self.chunk_duration = chunk_duration
        self.max_memory_mb = max_memory_mb
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.temp_files = []  # クリーンアップ用
        
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了時のクリーンアップ"""
        self.cleanup()
    
    def cleanup(self):
        """一時ファイルのクリーンアップ"""
        for temp_file in self.temp_files:
            try:
                if Path(temp_file).exists():
                    os.unlink(temp_file)
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file}: {e}")
        self.temp_files.clear()
        gc.collect()  # ガベージコレクション
    
    def check_memory_usage(self) -> bool:
        """メモリ使用量をチェック"""
        try:
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            if memory_usage > self.max_memory_mb:
                logger.warning(f"Memory usage high: {memory_usage:.1f}MB > {self.max_memory_mb}MB")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check memory usage: {e}")
            return True  # エラーの場合は続行
    
    def split_audio_file(self, input_path: str) -> Iterator[Dict[str, Any]]:
        """
        音声ファイルをチャンクに分割してストリーミング処理
        
        Args:
            input_path: 入力音声ファイルパス
            
        Yields:
            Dict[str, Any]: チャンク情報
        """
        try:
            # 入力ファイルの妥当性チェック
            is_valid, error_msg = validate_audio_file(input_path)
            if not is_valid:
                raise ValueError(f"Invalid input audio file: {error_msg}")
            
            # 音声メタデータを取得
            metadata = get_audio_metadata(input_path)
            total_duration = metadata['duration']
            
            if total_duration <= 0:
                raise ValueError("Invalid audio duration")
            
            logger.info(f"Splitting audio file: {input_path} (duration: {total_duration:.2f}s)")
            
            # チャンク数を計算
            num_chunks = int((total_duration + self.chunk_duration - 1) // self.chunk_duration)
            
            for chunk_idx in range(num_chunks):
                # メモリ使用量をチェック
                if not self.check_memory_usage():
                    logger.warning("Memory usage too high, forcing garbage collection")
                    gc.collect()
                
                start_time = chunk_idx * self.chunk_duration
                end_time = min((chunk_idx + 1) * self.chunk_duration, total_duration)
                
                # チャンクファイル名を生成
                chunk_filename = f"chunk_{chunk_idx:04d}_{Path(input_path).stem}.wav"
                chunk_path = Path(self.temp_dir) / chunk_filename
                self.temp_files.append(str(chunk_path))
                
                # チャンクを抽出
                success = self._extract_chunk(input_path, str(chunk_path), start_time, end_time)
                
                if success:
                    chunk_metadata = get_audio_metadata(str(chunk_path))
                    
                    yield {
                        'chunk_index': chunk_idx,
                        'chunk_path': str(chunk_path),
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time,
                        'metadata': chunk_metadata,
                        'total_chunks': num_chunks
                    }
                else:
                    logger.error(f"Failed to extract chunk {chunk_idx}")
                    
        except Exception as e:
            logger.error(f"Failed to split audio file: {e}")
            raise
    
    def _extract_chunk(self, input_path: str, output_path: str, start_time: float, end_time: float) -> bool:
        """
        音声ファイルのチャンクを抽出
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            start_time: 開始時間（秒）
            end_time: 終了時間（秒）
            
        Returns:
            bool: 抽出成功の可否
        """
        try:
            import ffmpeg
            
            # 出力ディレクトリを作成
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # FFmpegでチャンクを抽出
            (
                ffmpeg
                .input(input_path, ss=start_time, t=end_time - start_time)
                .output(
                    output_path,
                    acodec='pcm_s16le',  # 16bit PCM
                    ar=16000,            # 16kHz
                    ac=1,                # モノラル
                    af="highpass=f=80,lowpass=f=8000,volume=1.2"  # 音声フィルタ
                )
                .run(quiet=True, overwrite_output=True)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract chunk {start_time}-{end_time}: {e}")
            return False
    
    def process_audio_stream(self, 
                           input_path: str, 
                           processor_func,
                           **kwargs) -> Iterator[Any]:
        """
        音声ファイルをストリーミング処理
        
        Args:
            input_path: 入力音声ファイルパス
            processor_func: 各チャンクを処理する関数
            **kwargs: プロセッサ関数に渡す追加引数
            
        Yields:
            Any: プロセッサ関数の結果
        """
        try:
            for chunk_info in self.split_audio_file(input_path):
                logger.info(f"Processing chunk {chunk_info['chunk_index'] + 1}/{chunk_info['total_chunks']}")
                
                # チャンクを処理
                result = processor_func(chunk_info, **kwargs)
                
                # メモリ使用量をチェック
                if not self.check_memory_usage():
                    logger.warning("Memory usage high, forcing garbage collection")
                    gc.collect()
                
                yield result
                
        except Exception as e:
            logger.error(f"Failed to process audio stream: {e}")
            raise
    
    def get_optimal_chunk_duration(self, file_duration: float, available_memory_mb: int) -> int:
        """
        ファイルの長さと利用可能メモリに基づいて最適なチャンク長を計算
        
        Args:
            file_duration: ファイルの長さ（秒）
            available_memory_mb: 利用可能メモリ（MB）
            
        Returns:
            int: 最適なチャンク長（秒）
        """
        # 基本的な計算：利用可能メモリの80%を使用
        safe_memory_mb = available_memory_mb * 0.8
        
        # 1分あたりの推定メモリ使用量（16kHz, 16bit, モノラル）
        memory_per_minute_mb = 1.8  # 約1.8MB/分
        
        # 最適なチャンク長を計算
        optimal_chunk_duration = int((safe_memory_mb / memory_per_minute_mb) * 60)
        
        # 最小5分、最大30分に制限
        optimal_chunk_duration = max(300, min(optimal_chunk_duration, 1800))
        
        # ファイルの長さを考慮
        if file_duration < optimal_chunk_duration:
            optimal_chunk_duration = int(file_duration)
        
        logger.info(f"Optimal chunk duration: {optimal_chunk_duration}s (file: {file_duration:.1f}s, memory: {available_memory_mb}MB)")
        return optimal_chunk_duration


def create_streaming_processor(file_duration: float, 
                             max_memory_mb: int = 1024,
                             temp_dir: Optional[str] = None) -> StreamingAudioProcessor:
    """
    ファイルの長さに基づいて最適化されたストリーミングプロセッサを作成
    
    Args:
        file_duration: ファイルの長さ（秒）
        max_memory_mb: 最大メモリ使用量（MB）
        temp_dir: 一時ディレクトリ
        
    Returns:
        StreamingAudioProcessor: 最適化されたプロセッサ
    """
    processor = StreamingAudioProcessor(
        max_memory_mb=max_memory_mb,
        temp_dir=temp_dir
    )
    
    # 最適なチャンク長を計算
    optimal_chunk_duration = processor.get_optimal_chunk_duration(file_duration, max_memory_mb)
    processor.chunk_duration = optimal_chunk_duration
    
    return processor
