"""
Google Cloud Storageアダプター

GCSとの連携を実装します。
"""

import os
import json
from typing import Optional, Dict, Any, List, BinaryIO
from pathlib import Path
from datetime import datetime, timedelta

from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError

from ...utils.logging import get_logger

logger = get_logger(__name__)


class GCSAdapter:
    """Google Cloud Storageアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        GCSアダプターを初期化
        
        Args:
            config: GCS設定
        """
        self.config = config or {}
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """GCSクライアントを初期化"""
        try:
            # 認証情報の設定
            credentials_path = self.config.get('credentials_path')
            if credentials_path and os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # クライアントを作成
            self.client = storage.Client(project=self.config.get('project_id'))
            
            # バケットを取得
            bucket_name = self.config.get('bucket_name')
            if bucket_name:
                self.bucket = self.client.bucket(bucket_name)
            
            logger.info("GCS client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    def upload_file(
        self, 
        local_path: str, 
        gcs_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        ファイルをアップロード
        
        Args:
            local_path: ローカルファイルパス
            gcs_path: GCS内のパス
            content_type: コンテンツタイプ
            metadata: メタデータ
            
        Returns:
            bool: アップロードの成功/失敗
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            
            # メタデータを設定
            if metadata:
                blob.metadata = metadata
            
            # コンテンツタイプを設定
            if content_type:
                blob.content_type = content_type
            
            # ファイルをアップロード
            blob.upload_from_filename(local_path)
            
            logger.info(f"File uploaded: {local_path} -> gs://{self.bucket.name}/{gcs_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    def upload_bytes(
        self, 
        data: bytes, 
        gcs_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        バイトデータをアップロード
        
        Args:
            data: アップロードするデータ
            gcs_path: GCS内のパス
            content_type: コンテンツタイプ
            metadata: メタデータ
            
        Returns:
            bool: アップロードの成功/失敗
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            
            # メタデータを設定
            if metadata:
                blob.metadata = metadata
            
            # コンテンツタイプを設定
            if content_type:
                blob.content_type = content_type
            
            # データをアップロード
            blob.upload_from_string(data)
            
            logger.info(f"Bytes uploaded: {len(data)} bytes -> gs://{self.bucket.name}/{gcs_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload bytes: {e}")
            return False
    
    def download_file(
        self, 
        gcs_path: str, 
        local_path: str
    ) -> bool:
        """
        ファイルをダウンロード
        
        Args:
            gcs_path: GCS内のパス
            local_path: ローカル保存パス
            
        Returns:
            bool: ダウンロードの成功/失敗
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            
            # ファイルをダウンロード
            blob.download_to_filename(local_path)
            
            logger.info(f"File downloaded: gs://{self.bucket.name}/{gcs_path} -> {local_path}")
            return True
            
        except NotFound:
            logger.error(f"File not found: gs://{self.bucket.name}/{gcs_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    def download_bytes(
        self, 
        gcs_path: str
    ) -> Optional[bytes]:
        """
        バイトデータをダウンロード
        
        Args:
            gcs_path: GCS内のパス
            
        Returns:
            Optional[bytes]: ダウンロードしたデータ
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            
            # データをダウンロード
            data = blob.download_as_bytes()
            
            logger.info(f"Bytes downloaded: {len(data)} bytes from gs://{self.bucket.name}/{gcs_path}")
            return data
            
        except NotFound:
            logger.error(f"File not found: gs://{self.bucket.name}/{gcs_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to download bytes: {e}")
            return None
    
    def delete_file(
        self, 
        gcs_path: str
    ) -> bool:
        """
        ファイルを削除
        
        Args:
            gcs_path: GCS内のパス
            
        Returns:
            bool: 削除の成功/失敗
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            blob.delete()
            
            logger.info(f"File deleted: gs://{self.bucket.name}/{gcs_path}")
            return True
            
        except NotFound:
            logger.warning(f"File not found for deletion: gs://{self.bucket.name}/{gcs_path}")
            return True  # 既に存在しない場合は成功とする
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def list_files(
        self, 
        prefix: str = "",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        ファイル一覧を取得
        
        Args:
            prefix: プレフィックス
            max_results: 最大取得数
            
        Returns:
            List[Dict[str, Any]]: ファイル情報のリスト
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blobs = self.bucket.list_blobs(prefix=prefix, max_results=max_results)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'metadata': blob.metadata or {}
                })
            
            logger.info(f"Listed {len(files)} files with prefix: {prefix}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def get_file_info(
        self, 
        gcs_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        ファイル情報を取得
        
        Args:
            gcs_path: GCS内のパス
            
        Returns:
            Optional[Dict[str, Any]]: ファイル情報
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            blob.reload()  # 最新の情報を取得
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'metadata': blob.metadata or {}
            }
            
        except NotFound:
            logger.error(f"File not found: gs://{self.bucket.name}/{gcs_path}")
            return None
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None
    
    def generate_signed_url(
        self, 
        gcs_path: str,
        expiration: Optional[datetime] = None,
        method: str = "GET"
    ) -> Optional[str]:
        """
        署名付きURLを生成
        
        Args:
            gcs_path: GCS内のパス
            expiration: 有効期限
            method: HTTPメソッド
            
        Returns:
            Optional[str]: 署名付きURL
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            blob = self.bucket.blob(gcs_path)
            
            # デフォルトの有効期限（1時間）
            if expiration is None:
                expiration = datetime.utcnow() + timedelta(hours=1)
            
            # 署名付きURLを生成
            url = blob.generate_signed_url(
                expiration=expiration,
                method=method
            )
            
            logger.info(f"Generated signed URL for: gs://{self.bucket.name}/{gcs_path}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None
    
    def create_bucket(
        self, 
        bucket_name: str,
        location: Optional[str] = None
    ) -> bool:
        """
        バケットを作成
        
        Args:
            bucket_name: バケット名
            location: ロケーション
            
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            if not self.client:
                raise ValueError("Client not initialized")
            
            bucket = self.client.bucket(bucket_name)
            
            # バケットを作成
            bucket = self.client.create_bucket(
                bucket,
                location=location or self.config.get('region', 'asia-northeast1')
            )
            
            logger.info(f"Bucket created: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            return False
    
    def set_lifecycle_rules(
        self, 
        rules: List[Dict[str, Any]]
    ) -> bool:
        """
        ライフサイクルルールを設定
        
        Args:
            rules: ライフサイクルルール
            
        Returns:
            bool: 設定の成功/失敗
        """
        try:
            if not self.bucket:
                raise ValueError("Bucket not initialized")
            
            # ライフサイクルルールを設定
            self.bucket.lifecycle_rules = rules
            self.bucket.patch()
            
            logger.info(f"Lifecycle rules set: {len(rules)} rules")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set lifecycle rules: {e}")
            return False
