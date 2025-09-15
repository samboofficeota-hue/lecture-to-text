"""
Cloud Loggingアダプター

Cloud Loggingとの連携を実装します。
"""

import json
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from google.cloud import logging as cloud_logging
from google.cloud.logging.resource import Resource

from ...utils.logging import get_logger

logger = get_logger(__name__)


class LogLevel(Enum):
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CloudLoggingAdapter:
    """Cloud Loggingアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Cloud Loggingアダプターを初期化
        
        Args:
            config: ログ管理設定
        """
        self.config = config or {}
        self.client = None
        self.logger = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Cloud Loggingクライアントを初期化"""
        try:
            # クライアントを作成
            self.client = cloud_logging.Client(project=self.config.get('project_id'))
            
            # ログ名を設定
            log_name = self.config.get('log_name', 'darwin-app')
            
            # リソースを設定
            resource = Resource(
                type=self.config.get('resource_type', 'cloud_run_revision'),
                labels={
                    'service_name': self.config.get('service_name', 'darwin'),
                    'revision_name': self.config.get('version', '1.0.0'),
                    'location': self.config.get('region', 'asia-northeast1')
                }
            )
            
            # ロガーを作成
            self.logger = self.client.logger(log_name)
            self.logger.resource = resource
            
            # ラベルを設定
            self.logger.labels = self.config.get('labels', {})
            
            logger.info("Cloud Logging client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Logging client: {e}")
            # フォールバック：ローカルログのみ使用
            self.client = None
            self.logger = None
    
    def log(
        self, 
        level: LogLevel,
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        ログを出力
        
        Args:
            level: ログレベル
            message: メッセージ
            labels: ラベル
            metadata: メタデータ
            
        Returns:
            bool: 出力の成功/失敗
        """
        try:
            if not self.logger:
                # フォールバック：ローカルログのみ
                self._log_fallback(level, message, labels, metadata)
                return True
            
            # ログエントリを作成
            log_entry = {
                'message': message,
                'severity': level.value,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'labels': labels or {},
                'metadata': metadata or {}
            }
            
            # ログを出力
            self.logger.log_struct(log_entry)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log to Cloud Logging: {e}")
            # フォールバック：ローカルログのみ
            self._log_fallback(level, message, labels, metadata)
            return False
    
    def debug(
        self, 
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """DEBUGログを出力"""
        return self.log(LogLevel.DEBUG, message, labels, metadata)
    
    def info(
        self, 
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """INFOログを出力"""
        return self.log(LogLevel.INFO, message, labels, metadata)
    
    def warning(
        self, 
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """WARNINGログを出力"""
        return self.log(LogLevel.WARNING, message, labels, metadata)
    
    def error(
        self, 
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> bool:
        """ERRORログを出力"""
        if exception:
            metadata = metadata or {}
            metadata['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        return self.log(LogLevel.ERROR, message, labels, metadata)
    
    def critical(
        self, 
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> bool:
        """CRITICALログを出力"""
        if exception:
            metadata = metadata or {}
            metadata['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        return self.log(LogLevel.CRITICAL, message, labels, metadata)
    
    def log_lecture_processing(
        self, 
        lecture_id: str,
        stage: str,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        講義処理ログを出力
        
        Args:
            lecture_id: 講義ID
            stage: 処理段階
            status: ステータス
            message: メッセージ
            metadata: メタデータ
            
        Returns:
            bool: 出力の成功/失敗
        """
        labels = {
            'lecture_id': lecture_id,
            'stage': stage,
            'status': status
        }
        
        return self.info(message, labels, metadata)
    
    def log_api_request(
        self, 
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        APIリクエストログを出力
        
        Args:
            method: HTTPメソッド
            endpoint: エンドポイント
            status_code: ステータスコード
            response_time: レスポンス時間
            user_id: ユーザーID
            metadata: メタデータ
            
        Returns:
            bool: 出力の成功/失敗
        """
        labels = {
            'method': method,
            'endpoint': endpoint,
            'status_code': str(status_code),
            'user_id': user_id or 'anonymous'
        }
        
        log_metadata = {
            'response_time_ms': response_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if metadata:
            log_metadata.update(metadata)
        
        # ステータスコードに応じてログレベルを決定
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        return self.log(level, f"API Request: {method} {endpoint}", labels, log_metadata)
    
    def log_error_report(
        self, 
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        エラーレポートを出力
        
        Args:
            error: エラー
            context: コンテキスト
            
        Returns:
            bool: 出力の成功/失敗
        """
        labels = {
            'error_type': type(error).__name__,
            'service': self.config.get('service_name', 'darwin')
        }
        
        metadata = {
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.critical(f"Error Report: {type(error).__name__}", labels, metadata, error)
    
    def _log_fallback(
        self, 
        level: LogLevel,
        message: str,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """フォールバック：ローカルログのみ"""
        log_data = {
            'level': level.value,
            'message': message,
            'labels': labels or {},
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # ローカルログに出力
        if level == LogLevel.DEBUG:
            logger.debug(json.dumps(log_data, ensure_ascii=False))
        elif level == LogLevel.INFO:
            logger.info(json.dumps(log_data, ensure_ascii=False))
        elif level == LogLevel.WARNING:
            logger.warning(json.dumps(log_data, ensure_ascii=False))
        elif level == LogLevel.ERROR:
            logger.error(json.dumps(log_data, ensure_ascii=False))
        elif level == LogLevel.CRITICAL:
            logger.critical(json.dumps(log_data, ensure_ascii=False))
    
    def get_logs(
        self, 
        filter_str: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        ログを取得
        
        Args:
            filter_str: フィルタ文字列
            max_results: 最大取得数
            
        Returns:
            List[Dict[str, Any]]: ログエントリのリスト
        """
        try:
            if not self.client:
                return []
            
            # デフォルトフィルタ
            if not filter_str:
                filter_str = f'resource.type="{self.config.get("resource_type", "cloud_run_revision")}"'
            
            # ログを取得
            entries = self.client.list_entries(filter_=filter_str, max_results=max_results)
            
            logs = []
            for entry in entries:
                logs.append({
                    'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
                    'severity': entry.severity,
                    'message': entry.payload,
                    'labels': entry.labels,
                    'resource': entry.resource,
                    'log_name': entry.log_name
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    def get_error_logs(
        self, 
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        エラーログを取得
        
        Args:
            max_results: 最大取得数
            
        Returns:
            List[Dict[str, Any]]: エラーログのリスト
        """
        filter_str = f'resource.type="{self.config.get("resource_type", "cloud_run_revision")}" AND severity>=ERROR'
        return self.get_logs(filter_str, max_results)
