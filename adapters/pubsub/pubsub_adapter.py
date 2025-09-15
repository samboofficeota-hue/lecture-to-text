"""
Pub/Subアダプター

Cloud Pub/Subとの連携を実装します。
"""

import json
import threading
import time
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.cloud.pubsub_v1.subscriber.message import Message

from utils.logging import get_logger

logger = get_logger(__name__)


class MessageType(Enum):
    """メッセージタイプ"""
    LECTURE_PROCESSING = "lecture_processing"
    RAG_PROCESSING = "rag_processing"
    NOTIFICATION = "notification"
    SYSTEM_EVENT = "system_event"


class PubSubAdapter:
    """Pub/Subアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Pub/Subアダプターを初期化
        
        Args:
            config: Pub/Sub設定
        """
        self.config = config or {}
        self.publisher = None
        self.subscriber = None
        self.topic_path = None
        self.subscription_path = None
        self._message_handlers = {}
        self._running = False
        self._thread = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Pub/Subクライアントを初期化"""
        try:
            # パブリッシャーを作成
            self.publisher = PublisherClient()
            
            # サブスクライバーを作成
            self.subscriber = SubscriberClient()
            
            # パスを設定
            project_id = self.config.get('project_id')
            topic_name = self.config.get('topic_name', 'darwin-topic')
            subscription_name = self.config.get('subscription_name', 'darwin-subscription')
            
            self.topic_path = self.publisher.topic_path(project_id, topic_name)
            self.subscription_path = self.subscriber.subscription_path(project_id, subscription_name)
            
            logger.info(f"Pub/Sub clients initialized: {self.topic_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pub/Sub clients: {e}")
            raise
    
    def create_topic(self) -> bool:
        """
        トピックを作成
        
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            if not self.publisher or not self.topic_path:
                return False
            
            # トピックを作成
            self.publisher.create_topic(name=self.topic_path)
            logger.info(f"Topic created: {self.topic_path}")
            return True
            
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Topic already exists: {self.topic_path}")
                return True
            else:
                logger.error(f"Failed to create topic: {e}")
                return False
    
    def create_subscription(self) -> bool:
        """
        サブスクリプションを作成
        
        Returns:
            bool: 作成の成功/失敗
        """
        try:
            if not self.subscriber or not self.subscription_path or not self.topic_path:
                return False
            
            # サブスクリプションを作成
            self.subscriber.create_subscription(
                name=self.subscription_path,
                topic=self.topic_path,
                ack_deadline_seconds=self.config.get('ack_deadline_seconds', 600),
                message_retention_duration=self.config.get('message_retention_duration', 7) * 24 * 60 * 60,  # 日数を秒に変換
                enable_message_ordering=self.config.get('enable_message_ordering', False)
            )
            logger.info(f"Subscription created: {self.subscription_path}")
            return True
            
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"Subscription already exists: {self.subscription_path}")
                return True
            else:
                logger.error(f"Failed to create subscription: {e}")
                return False
    
    def publish_message(
        self, 
        message_type: MessageType,
        data: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        メッセージを発行
        
        Args:
            message_type: メッセージタイプ
            data: データ
            attributes: 属性
            
        Returns:
            Optional[str]: メッセージID
        """
        try:
            if not self.publisher or not self.topic_path:
                return None
            
            # メッセージデータを作成
            message_data = {
                'type': message_type.value,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            # メッセージを発行
            future = self.publisher.publish(
                self.topic_path,
                json.dumps(message_data).encode('utf-8'),
                **(attributes or {})
            )
            
            message_id = future.result()
            logger.info(f"Message published: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return None
    
    def publish_lecture_processing_message(
        self, 
        lecture_id: str,
        audio_file_path: str,
        pdf_file_path: Optional[str] = None,
        domain: str = "general"
    ) -> Optional[str]:
        """
        講義処理メッセージを発行
        
        Args:
            lecture_id: 講義ID
            audio_file_path: 音声ファイルパス
            pdf_file_path: PDFファイルパス
            domain: 分野
            
        Returns:
            Optional[str]: メッセージID
        """
        data = {
            'lecture_id': lecture_id,
            'audio_file_path': audio_file_path,
            'pdf_file_path': pdf_file_path,
            'domain': domain
        }
        
        attributes = {
            'lecture_id': lecture_id,
            'domain': domain,
            'message_type': MessageType.LECTURE_PROCESSING.value
        }
        
        return self.publish_message(MessageType.LECTURE_PROCESSING, data, attributes)
    
    def publish_rag_processing_message(
        self, 
        lecture_id: str,
        text_content: str,
        domain: str = "general"
    ) -> Optional[str]:
        """
        RAG処理メッセージを発行
        
        Args:
            lecture_id: 講義ID
            text_content: テキスト内容
            domain: 分野
            
        Returns:
            Optional[str]: メッセージID
        """
        data = {
            'lecture_id': lecture_id,
            'text_content': text_content,
            'domain': domain
        }
        
        attributes = {
            'lecture_id': lecture_id,
            'domain': domain,
            'message_type': MessageType.RAG_PROCESSING.value
        }
        
        return self.publish_message(MessageType.RAG_PROCESSING, data, attributes)
    
    def publish_notification_message(
        self, 
        user_id: str,
        message: str,
        notification_type: str = "info"
    ) -> Optional[str]:
        """
        通知メッセージを発行
        
        Args:
            user_id: ユーザーID
            message: メッセージ
            notification_type: 通知タイプ
            
        Returns:
            Optional[str]: メッセージID
        """
        data = {
            'user_id': user_id,
            'message': message,
            'notification_type': notification_type
        }
        
        attributes = {
            'user_id': user_id,
            'notification_type': notification_type,
            'message_type': MessageType.NOTIFICATION.value
        }
        
        return self.publish_message(MessageType.NOTIFICATION, data, attributes)
    
    def register_message_handler(
        self, 
        message_type: MessageType,
        handler: Callable[[Dict[str, Any], Dict[str, str]], bool]
    ):
        """
        メッセージハンドラーを登録
        
        Args:
            message_type: メッセージタイプ
            handler: ハンドラー関数
        """
        self._message_handlers[message_type] = handler
        logger.info(f"Message handler registered: {message_type.value}")
    
    def start_listening(self):
        """メッセージリスニングを開始"""
        if self._running:
            logger.warning("Already listening for messages")
            return
        
        if not self.subscriber or not self.subscription_path:
            logger.error("Subscriber not initialized")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._listen_for_messages)
        self._thread.start()
        logger.info("Started listening for messages")
    
    def stop_listening(self):
        """メッセージリスニングを停止"""
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("Stopped listening for messages")
    
    def _listen_for_messages(self):
        """メッセージをリスニング"""
        try:
            while self._running:
                # メッセージを取得
                response = self.subscriber.pull(
                    request={
                        'subscription': self.subscription_path,
                        'max_messages': 10
                    },
                    timeout=1.0
                )
                
                if not response.received_messages:
                    continue
                
                # メッセージを処理
                for message in response.received_messages:
                    self._process_message(message)
                
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
    
    def _process_message(self, message: Message):
        """メッセージを処理"""
        try:
            # メッセージデータを解析
            message_data = json.loads(message.data.decode('utf-8'))
            message_type = message_data.get('type')
            data = message_data.get('data', {})
            attributes = dict(message.attributes)
            
            # メッセージタイプを取得
            try:
                msg_type = MessageType(message_type)
            except ValueError:
                logger.error(f"Unknown message type: {message_type}")
                message.ack()
                return
            
            # ハンドラーを取得
            handler = self._message_handlers.get(msg_type)
            if not handler:
                logger.warning(f"No handler for message type: {message_type}")
                message.ack()
                return
            
            # ハンドラーを実行
            try:
                success = handler(data, attributes)
                if success:
                    message.ack()
                    logger.info(f"Message processed successfully: {message.message_id}")
                else:
                    message.nack()
                    logger.warning(f"Message processing failed: {message.message_id}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                message.nack()
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message.nack()
    
    def get_subscription_info(self) -> Optional[Dict[str, Any]]:
        """
        サブスクリプション情報を取得
        
        Returns:
            Optional[Dict[str, Any]]: サブスクリプション情報
        """
        try:
            if not self.subscriber or not self.subscription_path:
                return None
            
            subscription = self.subscriber.get_subscription(
                subscription=self.subscription_path
            )
            
            return {
                'name': subscription.name,
                'topic': subscription.topic,
                'ack_deadline_seconds': subscription.ack_deadline_seconds,
                'message_retention_duration': subscription.message_retention_duration.total_seconds(),
                'enable_message_ordering': subscription.enable_message_ordering
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription info: {e}")
            return None
    
    def get_topic_info(self) -> Optional[Dict[str, Any]]:
        """
        トピック情報を取得
        
        Returns:
            Optional[Dict[str, Any]]: トピック情報
        """
        try:
            if not self.publisher or not self.topic_path:
                return None
            
            topic = self.publisher.get_topic(topic=self.topic_path)
            
            return {
                'name': topic.name,
                'message_retention_duration': topic.message_retention_duration.total_seconds(),
                'kms_key_name': topic.kms_key_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get topic info: {e}")
            return None
