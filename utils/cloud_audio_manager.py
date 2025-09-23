"""
クラウド音声管理ユーティリティ

音声ファイルのチャンクをクラウドストレージ（GCS）で管理し、
システム的に参照しやすい状態を提供します。
"""

import os
import json
import tempfile
from typing import Dict, Any, List, Optional, Iterator
from pathlib import Path
from datetime import datetime
import uuid

from google.cloud import storage
from google.cloud.exceptions import NotFound

from utils.logging import get_logger
from utils.audio_utils import get_audio_metadata, validate_audio_file

logger = get_logger(__name__)


class CloudAudioManager:
    """クラウド音声管理クラス"""
    
    def __init__(self, 
                 bucket_name: str,
                 project_id: Optional[str] = None,
                 base_path: str = "audio_chunks"):
        """
        クラウド音声マネージャーを初期化
        
        Args:
            bucket_name: GCSバケット名
            project_id: GCPプロジェクトID
            base_path: ベースパス
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.base_path = base_path
        
        # GCSクライアントを初期化
        try:
            self.client = storage.Client(project=project_id)
            self.bucket = self.client.bucket(bucket_name)
            logger.info(f"GCS client initialized: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    def create_audio_session(self, 
                           original_filename: str,
                           duration: float,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        音声セッションを作成
        
        Args:
            original_filename: 元のファイル名
            duration: 音声の長さ（秒）
            metadata: 追加メタデータ
            
        Returns:
            str: セッションID
        """
        session_id = str(uuid.uuid4())
        
        # セッション情報を作成
        session_info = {
            'session_id': session_id,
            'original_filename': original_filename,
            'duration': duration,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'processing',
            'chunks': [],
            'metadata': metadata or {}
        }
        
        # セッション情報をGCSに保存
        session_path = f"{self.base_path}/{session_id}/session.json"
        blob = self.bucket.blob(session_path)
        blob.upload_from_string(
            json.dumps(session_info, indent=2),
            content_type='application/json'
        )
        
        logger.info(f"Audio session created: {session_id}")
        return session_id
    
    def upload_chunk(self, 
                    session_id: str,
                    chunk_index: int,
                    chunk_path: str,
                    start_time: float,
                    end_time: float) -> Dict[str, Any]:
        """
        音声チャンクをアップロード
        
        Args:
            session_id: セッションID
            chunk_index: チャンクインデックス
            chunk_path: チャンクファイルパス
            start_time: 開始時間
            end_time: 終了時間
            
        Returns:
            Dict[str, Any]: アップロード結果
        """
        try:
            # チャンクファイルの妥当性をチェック
            is_valid, error_msg = validate_audio_file(chunk_path)
            if not is_valid:
                raise ValueError(f"Invalid chunk file: {error_msg}")
            
            # チャンクメタデータを取得
            chunk_metadata = get_audio_metadata(chunk_path)
            
            # GCSパスを生成
            chunk_filename = f"chunk_{chunk_index:04d}.wav"
            gcs_path = f"{self.base_path}/{session_id}/chunks/{chunk_filename}"
            
            # チャンクをアップロード
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_filename(chunk_path)
            
            # チャンク情報を作成
            chunk_info = {
                'chunk_index': chunk_index,
                'gcs_path': gcs_path,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'file_size': chunk_metadata['file_size'],
                'sample_rate': chunk_metadata['sample_rate'],
                'channels': chunk_metadata['channels'],
                'bit_depth': chunk_metadata['bit_depth'],
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            # セッション情報を更新
            self._update_session_chunk(session_id, chunk_info)
            
            logger.info(f"Chunk uploaded: {session_id}/{chunk_filename}")
            return chunk_info
            
        except Exception as e:
            logger.error(f"Failed to upload chunk {chunk_index}: {e}")
            raise
    
    def download_chunk(self, 
                      session_id: str, 
                      chunk_index: int,
                      local_path: Optional[str] = None) -> str:
        """
        音声チャンクをダウンロード
        
        Args:
            session_id: セッションID
            chunk_index: チャンクインデックス
            local_path: ローカル保存パス（指定しない場合は一時ファイル）
            
        Returns:
            str: ローカルファイルパス
        """
        try:
            # セッション情報を取得
            session_info = self.get_session_info(session_id)
            chunk_info = session_info['chunks'][chunk_index]
            
            # ローカルパスを生成
            if local_path is None:
                temp_dir = tempfile.gettempdir()
                local_path = os.path.join(temp_dir, f"chunk_{chunk_index:04d}_{session_id}.wav")
            
            # チャンクをダウンロード
            blob = self.bucket.blob(chunk_info['gcs_path'])
            blob.download_to_filename(local_path)
            
            logger.info(f"Chunk downloaded: {session_id}/chunk_{chunk_index:04d}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download chunk {chunk_index}: {e}")
            raise
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        セッション情報を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Dict[str, Any]: セッション情報
        """
        try:
            session_path = f"{self.base_path}/{session_id}/session.json"
            blob = self.bucket.blob(session_path)
            
            if not blob.exists():
                raise NotFound(f"Session not found: {session_id}")
            
            content = blob.download_as_text()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            raise
    
    def update_session_status(self, 
                            session_id: str, 
                            status: str,
                            additional_info: Optional[Dict[str, Any]] = None):
        """
        セッションステータスを更新
        
        Args:
            session_id: セッションID
            status: 新しいステータス
            additional_info: 追加情報
        """
        try:
            session_info = self.get_session_info(session_id)
            session_info['status'] = status
            session_info['updated_at'] = datetime.utcnow().isoformat()
            
            if additional_info:
                session_info.update(additional_info)
            
            # セッション情報を更新
            session_path = f"{self.base_path}/{session_id}/session.json"
            blob = self.bucket.blob(session_path)
            blob.upload_from_string(
                json.dumps(session_info, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"Session status updated: {session_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
            raise
    
    def list_session_chunks(self, session_id: str) -> List[Dict[str, Any]]:
        """
        セッションのチャンク一覧を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            List[Dict[str, Any]]: チャンク一覧
        """
        try:
            session_info = self.get_session_info(session_id)
            return session_info.get('chunks', [])
            
        except Exception as e:
            logger.error(f"Failed to list session chunks: {e}")
            raise
    
    def stream_chunks(self, session_id: str) -> Iterator[Dict[str, Any]]:
        """
        セッションのチャンクをストリーミング取得
        
        Args:
            session_id: セッションID
            
        Yields:
            Dict[str, Any]: チャンク情報
        """
        try:
            chunks = self.list_session_chunks(session_id)
            
            for chunk_info in chunks:
                # チャンクを一時的にダウンロード
                local_path = self.download_chunk(
                    session_id, 
                    chunk_info['chunk_index']
                )
                
                # チャンク情報にローカルパスを追加
                chunk_info['local_path'] = local_path
                
                yield chunk_info
                
        except Exception as e:
            logger.error(f"Failed to stream chunks: {e}")
            raise
    
    def merge_chunks(self, 
                    session_id: str, 
                    output_path: str,
                    sample_rate: int = 16000,
                    channels: int = 1) -> Dict[str, Any]:
        """
        セッションのチャンクをマージ
        
        Args:
            session_id: セッションID
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            
        Returns:
            Dict[str, Any]: マージ結果
        """
        try:
            import ffmpeg
            
            # セッション情報を取得
            session_info = self.get_session_info(session_id)
            chunks = session_info['chunks']
            
            if not chunks:
                raise ValueError("No chunks found in session")
            
            # チャンクをソート
            chunks.sort(key=lambda x: x['chunk_index'])
            
            # 一時ファイルパスを生成
            temp_chunk_paths = []
            
            try:
                # 各チャンクをダウンロード
                for chunk_info in chunks:
                    local_path = self.download_chunk(
                        session_id, 
                        chunk_info['chunk_index']
                    )
                    temp_chunk_paths.append(local_path)
                
                # 出力ディレクトリを作成
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # FFmpegでチャンクをマージ
                inputs = [ffmpeg.input(path) for path in temp_chunk_paths]
                
                (
                    ffmpeg
                    .concat(*inputs, v=0, a=1)
                    .output(
                        output_path,
                        acodec='pcm_s16le',
                        ar=sample_rate,
                        ac=channels
                    )
                    .run(quiet=True, overwrite_output=True)
                )
                
                # マージ結果のメタデータを取得
                output_metadata = get_audio_metadata(output_path)
                
                result = {
                    'session_id': session_id,
                    'output_path': output_path,
                    'total_chunks': len(chunks),
                    'duration': output_metadata['duration'],
                    'file_size': output_metadata['file_size'],
                    'sample_rate': output_metadata['sample_rate'],
                    'channels': output_metadata['channels']
                }
                
                logger.info(f"Chunks merged: {session_id} -> {output_path}")
                return result
                
            finally:
                # 一時ファイルをクリーンアップ
                for temp_path in temp_chunk_paths:
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to merge chunks: {e}")
            raise
    
    def delete_session(self, session_id: str):
        """
        セッションを削除
        
        Args:
            session_id: セッションID
        """
        try:
            # セッション内のすべてのファイルを削除
            prefix = f"{self.base_path}/{session_id}/"
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                blob.delete()
            
            logger.info(f"Session deleted: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise
    
    def _update_session_chunk(self, session_id: str, chunk_info: Dict[str, Any]):
        """セッション情報にチャンクを追加"""
        try:
            session_info = self.get_session_info(session_id)
            session_info['chunks'].append(chunk_info)
            session_info['updated_at'] = datetime.utcnow().isoformat()
            
            # セッション情報を更新
            session_path = f"{self.base_path}/{session_id}/session.json"
            blob = self.bucket.blob(session_path)
            blob.upload_from_string(
                json.dumps(session_info, indent=2),
                content_type='application/json'
            )
            
        except Exception as e:
            logger.error(f"Failed to update session chunk: {e}")
            raise
