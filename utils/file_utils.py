"""
ファイル操作ユーティリティ

ファイルの操作に関する共通機能を提供します。
"""

import os
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """ファイル操作ユーティリティ"""
    
    @staticmethod
    def ensure_dir(path: str) -> Path:
        """
        ディレクトリを作成（存在しない場合）
        
        Args:
            path: ディレクトリパス
            
        Returns:
            Path: 作成されたディレクトリのPathオブジェクト
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        ファイル情報を取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            Dict[str, Any]: ファイル情報
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'parent': str(path.parent)
        }
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        安全なファイル名を生成
        
        Args:
            filename: 元のファイル名
            
        Returns:
            str: 安全なファイル名
        """
        # 危険な文字を置換
        unsafe_chars = '<>:"/\\|?*'
        safe_filename = filename
        
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 連続するアンダースコアを単一に
        while '__' in safe_filename:
            safe_filename = safe_filename.replace('__', '_')
        
        # 先頭・末尾のアンダースコアを削除
        safe_filename = safe_filename.strip('_')
        
        return safe_filename
    
    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """
        ファイルをコピー
        
        Args:
            src: ソースファイルパス
            dst: コピー先ファイルパス
            
        Returns:
            bool: コピーの成功/失敗
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            # コピー先ディレクトリを作成
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルをコピー
            shutil.copy2(src_path, dst_path)
            
            logger.info(f"File copied: {src} -> {dst}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return False
    
    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """
        ファイルを移動
        
        Args:
            src: ソースファイルパス
            dst: 移動先ファイルパス
            
        Returns:
            bool: 移動の成功/失敗
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            # 移動先ディレクトリを作成
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルを移動
            shutil.move(str(src_path), str(dst_path))
            
            logger.info(f"File moved: {src} -> {dst}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        ファイルを削除
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 削除の成功/失敗
        """
        try:
            path = Path(file_path)
            
            if path.is_file():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"Directory deleted: {file_path}")
            else:
                logger.warning(f"Path not found: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        ファイルサイズをMB単位で取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            float: ファイルサイズ（MB）
        """
        try:
            size_bytes = Path(file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    @staticmethod
    def is_valid_audio_file(file_path: str) -> bool:
        """
        有効な音声ファイルかチェック
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 有効な音声ファイルか
        """
        valid_extensions = {'.mp3', '.wav', '.mp4', '.m4a', '.flac', '.aac'}
        return Path(file_path).suffix.lower() in valid_extensions
    
    @staticmethod
    def is_valid_pdf_file(file_path: str) -> bool:
        """
        有効なPDFファイルかチェック
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 有効なPDFファイルか
        """
        return Path(file_path).suffix.lower() == '.pdf'
    
    @staticmethod
    def list_files(
        directory: str, 
        pattern: str = "*", 
        recursive: bool = False
    ) -> List[str]:
        """
        ディレクトリ内のファイル一覧を取得
        
        Args:
            directory: ディレクトリパス
            pattern: ファイルパターン
            recursive: 再帰的に検索するか
            
        Returns:
            List[str]: ファイルパスのリスト
        """
        try:
            dir_path = Path(directory)
            
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            return [str(f) for f in files if f.is_file()]
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []


# 便利な関数
def ensure_dir(path: str) -> Path:
    """ディレクトリを作成（存在しない場合）"""
    return FileUtils.ensure_dir(path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """ファイル情報を取得"""
    return FileUtils.get_file_info(file_path)
