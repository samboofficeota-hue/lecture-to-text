"""
音声ファイル処理ユーティリティ

音声ファイルのメタデータ取得や検証を行うユーティリティ関数を提供します。
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import subprocess
import tempfile

from utils.logging import get_logger

logger = get_logger(__name__)


def get_audio_metadata(file_path: str) -> Dict[str, Any]:
    """
    音声ファイルのメタデータを取得する
    
    Args:
        file_path: 音声ファイルのパス
        
    Returns:
        Dict[str, Any]: 音声メタデータ
    """
    try:
        import ffmpeg
        
        # FFprobeを使用してメタデータを取得
        probe = ffmpeg.probe(file_path)
        
        # 音声ストリームを取得
        audio_stream = None
        for stream in probe['streams']:
            if stream['codec_type'] == 'audio':
                audio_stream = stream
                break
        
        if not audio_stream:
            raise ValueError("No audio stream found in file")
        
        # 基本情報を取得
        duration = float(audio_stream.get('duration', 0))
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        bit_rate = int(audio_stream.get('bit_rate', 0))
        codec_name = audio_stream.get('codec_name', '')
        
        # ビット深度を推定
        bit_depth = _estimate_bit_depth(audio_stream)
        
        # ファイルサイズ
        file_size = Path(file_path).stat().st_size
        
        metadata = {
            'duration': duration,
            'sample_rate': sample_rate,
            'channels': channels,
            'bit_rate': bit_rate,
            'bit_depth': bit_depth,
            'codec_name': codec_name,
            'file_size': file_size,
            'format': Path(file_path).suffix.lower(),
            'raw_metadata': audio_stream
        }
        
        logger.info(f"Audio metadata extracted: {file_path}")
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to get audio metadata: {e}")
        # フォールバック: 基本的な情報のみ
        return {
            'duration': 0.0,
            'sample_rate': 0,
            'channels': 0,
            'bit_rate': 0,
            'bit_depth': 0,
            'codec_name': 'unknown',
            'file_size': Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            'format': Path(file_path).suffix.lower(),
            'raw_metadata': {}
        }


def _estimate_bit_depth(audio_stream: Dict[str, Any]) -> int:
    """
    音声ストリームからビット深度を推定する
    
    Args:
        audio_stream: 音声ストリーム情報
        
    Returns:
        int: 推定されたビット深度
    """
    # ビットレートとサンプルレートから推定
    bit_rate = int(audio_stream.get('bit_rate', 0))
    sample_rate = int(audio_stream.get('sample_rate', 0))
    channels = int(audio_stream.get('channels', 1))
    
    if bit_rate > 0 and sample_rate > 0 and channels > 0:
        # ビット深度 = ビットレート / (サンプルレート * チャンネル数)
        estimated_bit_depth = bit_rate // (sample_rate * channels)
        return min(max(estimated_bit_depth, 8), 32)  # 8-32bitの範囲に制限
    
    # コーデック名から推定
    codec_name = audio_stream.get('codec_name', '').lower()
    if 'pcm' in codec_name:
        if '16' in codec_name:
            return 16
        elif '24' in codec_name:
            return 24
        elif '32' in codec_name:
            return 32
        else:
            return 16  # デフォルト
    elif 'aac' in codec_name:
        return 16  # AACは通常16bit
    elif 'mp3' in codec_name:
        return 16  # MP3は通常16bit
    
    return 16  # デフォルト


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    音声ファイルの妥当性を検証する
    
    Args:
        file_path: 音声ファイルのパス
        
    Returns:
        Tuple[bool, str]: (妥当性の結果, エラーメッセージ)
    """
    try:
        # ファイル存在チェック
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}"
        
        # ファイルサイズチェック
        file_size = Path(file_path).stat().st_size
        if file_size == 0:
            return False, "File is empty"
        
        # 最小ファイルサイズチェック（1KB）
        if file_size < 1024:
            return False, "File too small (less than 1KB)"
        
        # 音声ファイル形式チェック
        valid_extensions = {'.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.aiff', '.au'}
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in valid_extensions:
            return False, f"Unsupported audio format: {file_ext}"
        
        # FFmpegでファイルの妥当性をチェック
        try:
            import ffmpeg
            ffmpeg.probe(file_path)
        except Exception as e:
            return False, f"Invalid audio file: {str(e)}"
        
        # メタデータを取得して詳細チェック
        metadata = get_audio_metadata(file_path)
        
        # 音声の長さチェック
        if metadata['duration'] < 0.1:
            return False, "Audio duration too short (less than 0.1 seconds)"
        
        # サンプルレートチェック
        if metadata['sample_rate'] < 8000:
            return False, "Sample rate too low (less than 8kHz)"
        
        # チャンネル数チェック
        if metadata['channels'] < 1:
            return False, "Invalid channel count"
        
        return True, "Valid audio file"
        
    except Exception as e:
        logger.error(f"Audio validation error: {e}")
        return False, f"Validation error: {str(e)}"


def get_audio_duration(file_path: str) -> float:
    """
    音声ファイルの長さを取得する
    
    Args:
        file_path: 音声ファイルのパス
        
    Returns:
        float: 音声の長さ（秒）
    """
    try:
        metadata = get_audio_metadata(file_path)
        return metadata['duration']
    except Exception as e:
        logger.error(f"Failed to get audio duration: {e}")
        return 0.0


def convert_audio_format(
    input_path: str, 
    output_path: str, 
    sample_rate: int = 16000,
    channels: int = 1,
    bit_depth: int = 16,
    codec: str = 'pcm_s16le'
) -> bool:
    """
    音声ファイルの形式を変換する
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス
        sample_rate: サンプルレート
        channels: チャンネル数
        bit_depth: ビット深度
        codec: コーデック
        
    Returns:
        bool: 変換成功の可否
    """
    try:
        import ffmpeg
        
        # 出力ディレクトリを作成
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 音声フィルタを構築
        audio_filters = [
            f"highpass=f=80",      # ハイパスフィルタ
            f"lowpass=f=8000",     # ローパスフィルタ
            "volume=1.2"           # 音量調整
        ]
        
        # FFmpegで変換
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                ac=channels,                    # チャンネル数
                ar=sample_rate,                 # サンプルレート
                acodec=codec,                   # コーデック
                af=",".join(audio_filters),     # 音声フィルタ
                vn=None,                        # 動画を無効化
                y=None                          # 上書き確認を無効化
            )
            .run(quiet=True, overwrite_output=True)
        )
        
        logger.info(f"Audio converted: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return False


def is_audio_file(file_path: str) -> bool:
    """
    ファイルが音声ファイルかどうかを判定する
    
    Args:
        file_path: ファイルパス
        
    Returns:
        bool: 音声ファイルかどうか
    """
    try:
        valid_extensions = {'.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma', '.aiff', '.au'}
        file_ext = Path(file_path).suffix.lower()
        return file_ext in valid_extensions
    except Exception:
        return False
