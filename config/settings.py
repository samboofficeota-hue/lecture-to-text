"""
設定管理

環境変数や設定ファイルから設定を読み込み、管理します。
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WhisperConfig:
    """Whisper設定"""
    model: str = "large-v3"
    device: str = "auto"
    compute_type: str = "auto"
    language: str = "ja"
    beam_size: int = 5
    best_of: int = 5
    temperature: List[float] = field(default_factory=lambda: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    vad_filter: bool = True
    word_timestamps: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'model_size': self.model,
            'device': self.device,
            'compute_type': self.compute_type,
            'language': self.language,
            'beam_size': self.beam_size,
            'best_of': self.best_of,
            'temperature': self.temperature,
            'vad_filter': self.vad_filter,
            'word_timestamps': self.word_timestamps
        }


@dataclass
class OpenAIConfig:
    """OpenAI設定"""
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000
    timeout: int = 30


@dataclass
class RAGConfig:
    """RAG設定"""
    use_mygpt: bool = True
    use_chatgpt: bool = True
    knowledge_base_path: Optional[str] = None
    confidence_threshold: float = 0.8
    max_context_length: int = 4000


@dataclass
class StorageConfig:
    """ストレージ設定"""
    output_dir: str = "./output"
    temp_dir: str = "./temp"
    backup_dir: str = "./backup"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_formats: List[str] = field(default_factory=lambda: [".mp3", ".wav", ".mp4", ".m4a", ".pdf"])


@dataclass
class LoggingConfig:
    """ログ設定"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class Settings:
    """全体設定"""
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # プロジェクト設定
    project_name: str = "Darwin"
    version: str = "1.0.0"
    debug: bool = False
    
    def __post_init__(self):
        """初期化後の処理"""
        self._load_from_environment()
        self._validate_settings()
    
    def _load_from_environment(self):
        """環境変数から設定を読み込み"""
        # Whisper設定
        self.whisper.model = os.getenv("WHISPER_MODEL", self.whisper.model)
        self.whisper.device = os.getenv("WHISPER_DEVICE", self.whisper.device)
        self.whisper.compute_type = os.getenv("WHISPER_COMPUTE_TYPE", self.whisper.compute_type)
        
        # OpenAI設定
        self.openai.api_key = os.getenv("OPENAI_API_KEY", self.openai.api_key)
        self.openai.model = os.getenv("OPENAI_MODEL", self.openai.model)
        self.openai.temperature = float(os.getenv("OPENAI_TEMPERATURE", str(self.openai.temperature)))
        self.openai.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", str(self.openai.max_tokens)))
        
        # RAG設定
        self.rag.use_mygpt = os.getenv("RAG_USE_MYGPT", "true").lower() == "true"
        self.rag.use_chatgpt = os.getenv("RAG_USE_CHATGPT", "true").lower() == "true"
        self.rag.knowledge_base_path = os.getenv("RAG_KNOWLEDGE_BASE_PATH")
        
        # ストレージ設定
        self.storage.output_dir = os.getenv("OUTPUT_DIR", self.storage.output_dir)
        self.storage.temp_dir = os.getenv("TEMP_DIR", self.storage.temp_dir)
        self.storage.backup_dir = os.getenv("BACKUP_DIR", self.storage.backup_dir)
        
        # ログ設定
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        self.logging.file_path = os.getenv("LOG_FILE_PATH")
        
        # プロジェクト設定
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def _validate_settings(self):
        """設定の妥当性を検証"""
        # 必須設定のチェック
        if not self.openai.api_key and self.rag.use_chatgpt:
            print("Warning: OPENAI_API_KEY not set, ChatGPT features will be disabled")
        
        # ディレクトリの作成
        for dir_path in [self.storage.output_dir, self.storage.temp_dir, self.storage.backup_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_whisper_config(self) -> Dict[str, Any]:
        """Whisper設定を辞書形式で取得"""
        return {
            'model_size': self.whisper.model,
            'device': self.whisper.device,
            'compute_type': self.whisper.compute_type,
            'language': self.whisper.language,
            'beam_size': self.whisper.beam_size,
            'best_of': self.whisper.best_of,
            'temperature': self.whisper.temperature,
            'vad_filter': self.whisper.vad_filter,
            'word_timestamps': self.whisper.word_timestamps
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """OpenAI設定を辞書形式で取得"""
        return {
            'api_key': self.openai.api_key,
            'model': self.openai.model,
            'temperature': self.openai.temperature,
            'max_tokens': self.openai.max_tokens,
            'timeout': self.openai.timeout
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """RAG設定を辞書形式で取得"""
        return {
            'use_mygpt': self.rag.use_mygpt,
            'use_chatgpt': self.rag.use_chatgpt,
            'knowledge_base_path': self.rag.knowledge_base_path,
            'confidence_threshold': self.rag.confidence_threshold,
            'max_context_length': self.rag.max_context_length
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で取得"""
        return {
            'whisper': self.whisper.__dict__,
            'openai': self.openai.__dict__,
            'rag': self.rag.__dict__,
            'storage': self.storage.__dict__,
            'logging': self.logging.__dict__,
            'project_name': self.project_name,
            'version': self.version,
            'debug': self.debug
        }


# グローバル設定インスタンス
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """設定インスタンスを取得"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings():
    """設定を再読み込み"""
    global _settings
    _settings = Settings()
