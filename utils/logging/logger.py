"""
ログ管理

ログの設定と管理を行います。
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from ...config.settings import get_settings


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    ログ設定を初期化
    
    Args:
        level: ログレベル
        log_file: ログファイルパス
        format_string: ログフォーマット
    """
    settings = get_settings()
    
    # ログレベルを設定
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # ログフォーマットを設定
    if format_string is None:
        format_string = settings.logging.format
    
    # ログハンドラーを設定
    handlers = []
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(format_string))
    handlers.append(console_handler)
    
    # ファイルハンドラー（オプション）
    if log_file or settings.logging.file_path:
        file_path = log_file or settings.logging.file_path
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(format_string))
        handlers.append(file_handler)
    
    # ルートロガーを設定
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 新しいハンドラーを追加
    for handler in handlers:
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        logging.Logger: ロガーインスタンス
    """
    return logging.getLogger(name)
