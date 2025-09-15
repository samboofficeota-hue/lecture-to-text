"""
データベースアダプター

Cloud SQLとの連携を実装します。
"""

import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

from utils.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy Base
Base = declarative_base()


class LectureRecord(Base):
    """講義記録テーブル"""
    __tablename__ = 'lecture_records'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    status = Column(String, nullable=False, default='uploaded')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    lecture_metadata = Column(JSON)
    
    # ファイルパス
    audio_file_path = Column(String)
    pdf_file_path = Column(String)
    transcript_path = Column(String)
    final_transcript_path = Column(String)
    
    # 処理結果
    processing_result = Column(JSON)


class KnowledgeItem(Base):
    """知識アイテムテーブル"""
    __tablename__ = 'knowledge_items'
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    domain = Column(String, nullable=False)
    embedding = Column(JSON)  # pgvector用
    lecture_metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseAdapter:
    """データベースアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        データベースアダプターを初期化
        
        Args:
            config: データベース設定
        """
        self.config = config or {}
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """データベースエンジンを初期化"""
        try:
            # 接続文字列を取得
            connection_string = self.config.get('connection_string')
            if not connection_string:
                from .database_config import DatabaseConfig
                db_config = DatabaseConfig(**self.config)
                connection_string = db_config.get_connection_string()
            
            # エンジンを作成
            self.engine = create_engine(
                connection_string,
                pool_size=self.config.get('pool_size', 5),
                max_overflow=self.config.get('max_overflow', 10),
                pool_timeout=self.config.get('pool_timeout', 30),
                pool_recycle=self.config.get('pool_recycle', 3600),
                echo=self.config.get('echo', False)
            )
            
            # セッションファクトリを作成
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # テーブルを作成
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """データベースセッションを取得"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_lecture_record(
        self, 
        lecture_id: str,
        title: str,
        domain: str,
        audio_file_path: Optional[str] = None,
        pdf_file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        講義記録を作成
        
        Args:
            lecture_id: 講義ID
            title: タイトル
            domain: 分野
            audio_file_path: 音声ファイルパス
            pdf_file_path: PDFファイルパス
            metadata: メタデータ
            
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            with self.get_session() as session:
                lecture_record = LectureRecord(
                    id=lecture_id,
                    title=title,
                    domain=domain,
                    audio_file_path=audio_file_path,
                    pdf_file_path=pdf_file_path,
                    metadata=metadata or {}
                )
                
                session.add(lecture_record)
                session.commit()
                
                logger.info(f"Lecture record created: {lecture_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create lecture record: {e}")
            return False
    
    def get_lecture_record(
        self, 
        lecture_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        講義記録を取得
        
        Args:
            lecture_id: 講義ID
            
        Returns:
            Optional[Dict[str, Any]]: 講義記録
        """
        try:
            with self.get_session() as session:
                lecture_record = session.query(LectureRecord).filter(
                    LectureRecord.id == lecture_id
                ).first()
                
                if lecture_record:
                    return {
                        'id': lecture_record.id,
                        'title': lecture_record.title,
                        'domain': lecture_record.domain,
                        'status': lecture_record.status,
                        'created_at': lecture_record.created_at,
                        'updated_at': lecture_record.updated_at,
                        'metadata': lecture_record.metadata,
                        'audio_file_path': lecture_record.audio_file_path,
                        'pdf_file_path': lecture_record.pdf_file_path,
                        'transcript_path': lecture_record.transcript_path,
                        'final_transcript_path': lecture_record.final_transcript_path,
                        'processing_result': lecture_record.processing_result
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get lecture record: {e}")
            return None
    
    def update_lecture_record(
        self, 
        lecture_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        講義記録を更新
        
        Args:
            lecture_id: 講義ID
            updates: 更新内容
            
        Returns:
            bool: 更新の成功/失敗
        """
        try:
            with self.get_session() as session:
                lecture_record = session.query(LectureRecord).filter(
                    LectureRecord.id == lecture_id
                ).first()
                
                if lecture_record:
                    for key, value in updates.items():
                        if hasattr(lecture_record, key):
                            setattr(lecture_record, key, value)
                    
                    lecture_record.updated_at = datetime.utcnow()
                    session.commit()
                    
                    logger.info(f"Lecture record updated: {lecture_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to update lecture record: {e}")
            return False
    
    def list_lecture_records(
        self, 
        domain: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        講義記録一覧を取得
        
        Args:
            domain: 分野フィルタ
            status: ステータスフィルタ
            limit: 取得数制限
            offset: オフセット
            
        Returns:
            List[Dict[str, Any]]: 講義記録一覧
        """
        try:
            with self.get_session() as session:
                query = session.query(LectureRecord)
                
                if domain:
                    query = query.filter(LectureRecord.domain == domain)
                
                if status:
                    query = query.filter(LectureRecord.status == status)
                
                lecture_records = query.offset(offset).limit(limit).all()
                
                return [
                    {
                        'id': record.id,
                        'title': record.title,
                        'domain': record.domain,
                        'status': record.status,
                        'created_at': record.created_at,
                        'updated_at': record.updated_at,
                        'metadata': record.metadata
                    }
                    for record in lecture_records
                ]
                
        except Exception as e:
            logger.error(f"Failed to list lecture records: {e}")
            return []
    
    def create_knowledge_item(
        self, 
        knowledge_id: str,
        content: str,
        domain: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        知識アイテムを作成
        
        Args:
            knowledge_id: 知識ID
            content: 内容
            domain: 分野
            embedding: 埋め込みベクトル
            metadata: メタデータ
            
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            with self.get_session() as session:
                knowledge_item = KnowledgeItem(
                    id=knowledge_id,
                    content=content,
                    domain=domain,
                    embedding=embedding,
                    metadata=metadata or {}
                )
                
                session.add(knowledge_item)
                session.commit()
                
                logger.info(f"Knowledge item created: {knowledge_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create knowledge item: {e}")
            return False
    
    def search_knowledge_items(
        self, 
        query: str,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        知識アイテムを検索
        
        Args:
            query: 検索クエリ
            domain: 分野フィルタ
            limit: 取得数制限
            
        Returns:
            List[Dict[str, Any]]: 知識アイテム一覧
        """
        try:
            with self.get_session() as session:
                sql_query = session.query(KnowledgeItem).filter(
                    KnowledgeItem.content.contains(query)
                )
                
                if domain:
                    sql_query = sql_query.filter(KnowledgeItem.domain == domain)
                
                knowledge_items = sql_query.limit(limit).all()
                
                return [
                    {
                        'id': item.id,
                        'content': item.content,
                        'domain': item.domain,
                        'metadata': item.metadata,
                        'created_at': item.created_at
                    }
                    for item in knowledge_items
                ]
                
        except Exception as e:
            logger.error(f"Failed to search knowledge items: {e}")
            return []
    
    def vector_search(
        self, 
        query_embedding: List[float],
        domain: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        ベクタ検索を実行
        
        Args:
            query_embedding: クエリの埋め込みベクトル
            domain: 分野フィルタ
            limit: 取得数制限
            similarity_threshold: 類似度閾値
            
        Returns:
            List[Dict[str, Any]]: 検索結果
        """
        try:
            with self.get_session() as session:
                # pgvectorの類似度検索クエリ
                sql = text("""
                    SELECT id, content, domain, metadata, created_at,
                           (embedding <=> :query_embedding) as similarity
                    FROM knowledge_items
                    WHERE embedding <=> :query_embedding < :threshold
                    ORDER BY embedding <=> :query_embedding
                    LIMIT :limit
                """)
                
                if domain:
                    sql = text("""
                        SELECT id, content, domain, metadata, created_at,
                               (embedding <=> :query_embedding) as similarity
                        FROM knowledge_items
                        WHERE domain = :domain
                          AND embedding <=> :query_embedding < :threshold
                        ORDER BY embedding <=> :query_embedding
                        LIMIT :limit
                    """)
                
                result = session.execute(sql, {
                    'query_embedding': json.dumps(query_embedding),
                    'threshold': 1 - similarity_threshold,  # pgvectorは距離なので変換
                    'domain': domain,
                    'limit': limit
                })
                
                return [
                    {
                        'id': row.id,
                        'content': row.content,
                        'domain': row.domain,
                        'metadata': row.metadata,
                        'created_at': row.created_at,
                        'similarity': 1 - row.similarity  # 距離を類似度に変換
                    }
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"Failed to perform vector search: {e}")
            return []
    
    def execute_query(
        self, 
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        カスタムクエリを実行
        
        Args:
            query: SQLクエリ
            params: パラメータ
            
        Returns:
            List[Dict[str, Any]]: クエリ結果
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                
                return [dict(row) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        データベース統計を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        try:
            with self.get_session() as session:
                # 講義記録数
                lecture_count = session.query(LectureRecord).count()
                
                # 知識アイテム数
                knowledge_count = session.query(KnowledgeItem).count()
                
                # 分野別統計
                domain_stats = session.execute(text("""
                    SELECT domain, COUNT(*) as count
                    FROM lecture_records
                    GROUP BY domain
                """)).fetchall()
                
                return {
                    'lecture_records': lecture_count,
                    'knowledge_items': knowledge_count,
                    'domains': [{'domain': row.domain, 'count': row.count} for row in domain_stats]
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
