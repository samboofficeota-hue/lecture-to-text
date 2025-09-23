"""
新しいアーキテクチャ用Cloud Run API

既存のAPIと互換性を保ちながら、新しいアーキテクチャを活用します。
"""

import os
import json
import tempfile
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import hashlib
import hmac

# 新しいアーキテクチャのインポート
from core.services.lecture_processing_service import LectureProcessingService
from adapters.whisper.whisper_adapter import WhisperAdapter
from adapters.openai.openai_adapter import OpenAIAdapter
from adapters.file.file_adapter import FileAdapter
from adapters.mygpt.mygpt_adapter import MyGPTAdapter
from config.settings import get_settings

# ストリーミング処理のインポート
from utils.streaming_audio_processor import StreamingAudioProcessor, create_streaming_processor
from utils.cloud_audio_manager import CloudAudioManager
from utils.audio_utils import get_audio_metadata
import psutil

app = Flask(__name__)

# セキュリティ強化: 特定のOriginのみ許可
CORS(app, 
     origins=[
         "https://darwin.sambo-office.com",  # 本番ドメイン
         "https://lecture-to-text-7nbgp21xf-yoshis-projects-421cbceb.vercel.app",  # 現在のVercel URL
         "https://lecture-to-text-qov0p5jjn-yoshis-projects-421cbceb.vercel.app",
         "https://lecture-to-text.vercel.app",
         "https://lecture-to-text-omega.vercel.app",
         "https://lecture-to-text-7xtgo3bbl-yoshis-projects-421cbceb.vercel.app",
         "http://localhost:3000"  # 開発用
     ],
     allow_headers=["Content-Type", "X-API-Key", "Authorization"],
     allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     supports_credentials=True
)

# APIキー設定
API_KEY = os.getenv('NEXT_PUBLIC_API_KEY', 'default-secret-key-change-this')

# ファイルアップロードサイズ制限を設定（100MB）
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# ストリーミング処理の設定
MAX_MEMORY_MB = int(os.getenv('MAX_MEMORY_MB', '6144'))  # 6GB
CHUNK_DURATION = int(os.getenv('CHUNK_DURATION', '300'))  # 5分
ENABLE_STREAMING = os.getenv('ENABLE_STREAMING', 'true').lower() == 'true'
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'lecture-to-text-audio-chunks')

def get_memory_usage():
    """現在のメモリ使用量を取得（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def log_memory_usage(step_name):
    """メモリ使用量をログに出力"""
    memory_mb = get_memory_usage()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {step_name} - メモリ使用量: {memory_mb:.2f}MB / {MAX_MEMORY_MB}MB")
    if memory_mb > MAX_MEMORY_MB * 0.8:  # 80%を超えたら警告
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 警告: メモリ使用量が制限の80%を超えています")

def process_with_streaming(audio_path, title, temp_dir):
    """ストリーミング処理で音声ファイルを処理"""
    global processing_status
    
    try:
        # 音声ファイルのメタデータを取得
        audio_metadata = get_audio_metadata(audio_path)
        duration = audio_metadata['duration']
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ストリーミング処理開始: {duration:.2f}秒の音声を{CHUNK_DURATION}秒のチャンクに分割")
        log_memory_usage("ストリーミング処理開始")
        
        # ストリーミングプロセッサを作成
        with create_streaming_processor(
            file_duration=duration,
            max_memory_mb=MAX_MEMORY_MB,
            chunk_duration_sec=CHUNK_DURATION,
            temp_dir=temp_dir
        ) as processor:
            
            # Cloud Audio Managerを初期化
            cloud_manager = CloudAudioManager(GCS_BUCKET_NAME)
            
            # 音声セッションを作成
            session_id = cloud_manager.create_audio_session(
                original_filename=os.path.basename(audio_path),
                duration=duration,
                metadata=audio_metadata
            )
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声セッション作成: {session_id}")
            
            # 音声をチャンクに分割して処理
            all_transcripts = []
            all_technical_terms = []
            
            chunk_count = 0
            total_chunks = int(duration / CHUNK_DURATION) + 1
            
            for chunk_info in processor.split_audio_file(audio_path):
                chunk_count += 1
                processing_status["current_step"] = f"チャンク処理中... ({chunk_count}/{total_chunks})"
                processing_status["progress"] = 20 + (chunk_count / total_chunks) * 60
                
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] チャンク {chunk_count}/{total_chunks} 処理中: {chunk_info['duration']:.2f}秒")
                log_memory_usage(f"チャンク{chunk_count}処理開始")
                
                # チャンクをCloud Storageにアップロード
                cloud_manager.upload_chunk(
                    session_id=session_id,
                    chunk_index=chunk_info['chunk_index'],
                    chunk_path=chunk_info['chunk_path'],
                    start_time=chunk_info['start_time'],
                    end_time=chunk_info['end_time']
                )
                
                # チャンクを処理
                chunk_result = lecture_service.process_lecture(
                    audio_file_path=chunk_info['chunk_path'],
                    title=f"{title} (チャンク {chunk_count})",
                    domain="general"
                )
                
                # 結果を蓄積
                if chunk_result.transcription and chunk_result.transcription.text:
                    all_transcripts.append(chunk_result.transcription.text)
                
                if chunk_result.technical_terms:
                    all_technical_terms.extend(chunk_result.technical_terms)
                
                log_memory_usage(f"チャンク{chunk_count}処理完了")
                
                # チャンクファイルを削除してメモリを解放
                try:
                    os.remove(chunk_info['chunk_path'])
                except:
                    pass
            
            # 結果をマージ
            processing_status["current_step"] = "結果マージ中..."
            processing_status["progress"] = 85
            log_memory_usage("結果マージ開始")
            
            merged_transcript = "\n\n".join(all_transcripts)
            unique_technical_terms = list(set(all_technical_terms))
            
            # 結果オブジェクトを作成
            from core.models.lecture_result import LectureResult
            from core.models.transcription import Transcription
            
            merged_transcription = Transcription(
                text=merged_transcript,
                segments=[]  # チャンク処理ではセグメント情報は保持しない
            )
            
            result = LectureResult(
                title=title,
                audio_duration=duration,
                transcription=merged_transcription,
                processed_text=merged_transcript,
                enhanced_text=merged_transcript,
                technical_terms=unique_technical_terms,
                summary="",
                key_points=[],
                questions=[],
                created_at=None
            )
            
            log_memory_usage("結果マージ完了")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ストリーミング処理完了: {len(all_transcripts)}チャンク処理")
            
            return result
            
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ストリーミング処理エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@app.errorhandler(413)
def too_large(e):
    """ファイルサイズが大きすぎる場合のエラーハンドラー"""
    response = jsonify({"error": "File too large. Maximum size is 100MB"})
    return add_cors_headers(response), 413

@app.errorhandler(503)
def service_unavailable(e):
    """サービス利用不可エラーハンドラー"""
    response = jsonify({"error": "Service temporarily unavailable. Please try again later."})
    return add_cors_headers(response), 503

@app.errorhandler(500)
def internal_error(e):
    """内部サーバーエラーハンドラー"""
    response = jsonify({"error": "Internal server error. Please try again later."})
    return add_cors_headers(response), 500

@app.errorhandler(404)
def not_found(e):
    """404エラーハンドラー"""
    response = jsonify({"error": "Endpoint not found"})
    return add_cors_headers(response), 404

# 新しいアーキテクチャのサービス初期化
lecture_service = None

def init_services():
    """新しいアーキテクチャのサービスを初期化"""
    global lecture_service
    
    if lecture_service is None:
        try:
            print("新しいアーキテクチャのサービスを初期化中...")
            
            # 設定を取得
            settings = get_settings()
            print(f"設定取得完了: {settings}")
            
            # アダプターを初期化
            print("Whisperアダプターを初期化中...")
            whisper_adapter = WhisperAdapter(settings.whisper.to_dict())
            
            print("OpenAIアダプターを初期化中...")
            openai_adapter = OpenAIAdapter(settings.openai.to_dict())
            
            print("Fileアダプターを初期化中...")
            file_adapter = FileAdapter()
            
            print("MyGPTアダプターを初期化中...")
            mygpt_adapter = MyGPTAdapter(settings.mygpt.to_dict())
            
            # 講義処理サービスを初期化
            print("講義処理サービスを初期化中...")
            lecture_service = LectureProcessingService(
                audio_processor=whisper_adapter,
                transcriber=whisper_adapter,
                text_processor=openai_adapter,
                output_generator=openai_adapter,
                rag_interface=mygpt_adapter,
                pdf_processor=file_adapter
            )
            
            print("新しいアーキテクチャのサービス初期化完了")
        except Exception as e:
            print(f"サービス初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            raise

# 処理状況を追跡するためのグローバル変数
processing_status = {
    "is_processing": False,
    "current_step": "",
    "progress": 0,
    "total_steps": 0,
    "start_time": None,
    "error": None
}

def add_cors_headers(response):
    """レスポンスにCORSヘッダーを追加"""
    # flask-corsが既にCORSヘッダーを設定しているので、追加の設定は不要
    # 必要に応じて追加のヘッダーを設定
    return response

@app.route('/', methods=['GET'])
def root():
    """ルートパス"""
    response = jsonify({
        "message": "Darwin Lecture Assistant API",
        "version": "2.0.0",
        "architecture": "new",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "process_audio": "/process-audio"
        }
    })
    return add_cors_headers(response)

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    response = jsonify({"status": "healthy", "architecture": "new"})
    return add_cors_headers(response)

@app.route('/status', methods=['GET'])
def get_processing_status():
    """処理状況を取得"""
    global processing_status
    response = jsonify(processing_status)
    return add_cors_headers(response)

def verify_api_key():
    """APIキーを検証"""
    api_key = request.headers.get('X-API-Key')
    print(f"Received API Key: {api_key}")
    print(f"Expected API Key: {API_KEY}")
    print(f"Environment NEXT_PUBLIC_API_KEY: {os.getenv('NEXT_PUBLIC_API_KEY')}")
    
    if not api_key or api_key != API_KEY:
        response = jsonify({"error": "Invalid API key"})
        return add_cors_headers(response), 401
    return None

# OPTIONSハンドラーは不要（flask-corsが自動処理）

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """音声ファイル処理のメインエンドポイント（新しいアーキテクチャ）"""
    global processing_status
    
    try:
        # 既に処理中の場合はエラーを返す
        if processing_status["is_processing"]:
            response = jsonify({"error": "既に処理が実行中です"})
            return add_cors_headers(response), 409
        
        # 処理状況をリセット
        processing_status = {
            "is_processing": True,
            "current_step": "初期化中...",
            "progress": 0,
            "total_steps": 0,
            "start_time": time.time(),
            "error": None
        }
        
        # APIキー検証
        auth_error = verify_api_key()
        if auth_error:
            processing_status["is_processing"] = False
            processing_status["error"] = "Invalid API key"
            response = jsonify({"error": "Invalid API key"})
            return add_cors_headers(response), 401
        
        # ファイルアップロードを取得
        if 'audioFile' not in request.files:
            processing_status["is_processing"] = False
            processing_status["error"] = "audioFile is required"
            response = jsonify({"error": "audioFile is required"})
            return add_cors_headers(response), 400
        
        audio_file = request.files['audioFile']
        title = request.form.get('title', 'Untitled')
        
        if audio_file.filename == '':
            processing_status["is_processing"] = False
            processing_status["error"] = "No file selected"
            response = jsonify({"error": "No file selected"})
            return add_cors_headers(response), 400
        
        # ファイルサイズをチェック
        audio_file.seek(0, 2)  # ファイルの末尾に移動
        file_size = audio_file.tell()
        audio_file.seek(0)  # ファイルの先頭に戻す
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            processing_status["is_processing"] = False
            processing_status["error"] = "File too large"
            response = jsonify({"error": "File too large. Maximum size is 100MB"})
            return add_cors_headers(response), 413
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 新しいアーキテクチャで音声処理開始: {title}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ファイル名: {audio_file.filename}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ファイルサイズ: {file_size / 1024 / 1024:.2f} MB")
        
        # サービスを初期化
        processing_status["current_step"] = "サービス初期化中..."
        processing_status["progress"] = 5
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] サービス初期化中...")
        init_services()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] サービス初期化完了")
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            # 音声ファイルを保存
            processing_status["current_step"] = "音声ファイル保存中..."
            processing_status["progress"] = 10
            log_memory_usage("音声ファイル保存開始")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存中...")
            audio_path = os.path.join(temp_dir, "audio.mp3")
            audio_file.save(audio_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存完了")
            log_memory_usage("音声ファイル保存完了")
            
            # 音声ファイルのメタデータを取得
            audio_metadata = get_audio_metadata(audio_path)
            duration = audio_metadata['duration']
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル情報: 長さ={duration:.2f}秒, サイズ={audio_metadata['file_size']/1024/1024:.2f}MB")
            
            # ストリーミング処理を使用するかどうかを判定
            if ENABLE_STREAMING and duration > CHUNK_DURATION:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ストリーミング処理を開始 (長さ: {duration:.2f}秒 > {CHUNK_DURATION}秒)")
                result = process_with_streaming(audio_path, title, temp_dir)
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 通常処理を開始 (長さ: {duration:.2f}秒 <= {CHUNK_DURATION}秒)")
                # 通常の講義処理サービスを使用
                processing_status["current_step"] = "講義処理実行中..."
                processing_status["progress"] = 20
                log_memory_usage("講義処理開始")
                result = lecture_service.process_lecture(
                    audio_file_path=audio_path,
                    title=title,
                    domain="general"
                )
                log_memory_usage("講義処理完了")
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 講義処理完了")
            
            # 結果を返す
            processing_status["current_step"] = "処理完了"
            processing_status["progress"] = 100
            
            response = {
                "title": title,
                "audioFileName": audio_file.filename,
                "audioDuration": result.audio_duration,
                "segmentCount": len(result.transcription.segments) if result.transcription else 0,
                "firstDraft": result.transcription.text if result.transcription else "",
                "transcript": result.enhanced_text or result.processed_text,
                "technicalTerms": result.technical_terms or [],
                "status": "completed",
                "architecture": "new"
            }
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 処理完了 - 結果を返送中")
            
            # 処理状況をリセット
            processing_status["is_processing"] = False
            processing_status["current_step"] = ""
            processing_status["progress"] = 0
            
            response_obj = jsonify(response)
            return add_cors_headers(response_obj)
            
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] エラー: {str(e)}")
        import traceback
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] スタックトレース: {traceback.format_exc()}")
        
        # エラー時に処理状況をリセット
        processing_status["is_processing"] = False
        processing_status["error"] = str(e)
        processing_status["current_step"] = ""
        processing_status["progress"] = 0
        
        response = jsonify({"error": f"処理中にエラーが発生しました: {str(e)}"})
        return add_cors_headers(response), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
