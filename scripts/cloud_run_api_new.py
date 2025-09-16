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

app = Flask(__name__)

# セキュリティ強化: 特定のOriginのみ許可
CORS(app, origins=[
    "https://darwin.sambo-office.com",  # 本番ドメイン
    "https://lecture-to-text-7nbgp21xf-yoshis-projects-421cbceb.vercel.app",  # 現在のVercel URL
    "https://lecture-to-text-qov0p5jjn-yoshis-projects-421cbceb.vercel.app",
    "https://lecture-to-text.vercel.app",
    "https://lecture-to-text-omega.vercel.app",
    "https://lecture-to-text-7xtgo3bbl-yoshis-projects-421cbceb.vercel.app",
    "http://localhost:3000"  # 開発用
])

# APIキー設定
API_KEY = os.getenv('NEXT_PUBLIC_API_KEY', 'default-secret-key-change-this')

# ファイルアップロードサイズ制限を設定（100MB）
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

@app.errorhandler(413)
def too_large(e):
    """ファイルサイズが大きすぎる場合のエラーハンドラー"""
    return jsonify({"error": "File too large. Maximum size is 100MB"}), 413

# 新しいアーキテクチャのサービス初期化
lecture_service = None

def init_services():
    """新しいアーキテクチャのサービスを初期化"""
    global lecture_service
    
    if lecture_service is None:
        print("新しいアーキテクチャのサービスを初期化中...")
        
        # 設定を取得
        settings = get_settings()
        
        # アダプターを初期化
        whisper_adapter = WhisperAdapter(settings.whisper.to_dict())
        openai_adapter = OpenAIAdapter(settings.openai.to_dict())
        file_adapter = FileAdapter()
        mygpt_adapter = MyGPTAdapter(settings.mygpt.to_dict())
        
        # 講義処理サービスを初期化
        lecture_service = LectureProcessingService(
            whisper_adapter=whisper_adapter,
            openai_adapter=openai_adapter,
            file_adapter=file_adapter,
            mygpt_adapter=mygpt_adapter
        )
        
        print("新しいアーキテクチャのサービス初期化完了")

# 処理状況を追跡するためのグローバル変数
processing_status = {
    "is_processing": False,
    "current_step": "",
    "progress": 0,
    "total_steps": 0,
    "start_time": None,
    "error": None
}

@app.route('/', methods=['GET'])
def root():
    """ルートパス"""
    return jsonify({
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

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({"status": "healthy", "architecture": "new"})

@app.route('/status', methods=['GET'])
def get_processing_status():
    """処理状況を取得"""
    global processing_status
    return jsonify(processing_status)

def verify_api_key():
    """APIキーを検証"""
    api_key = request.headers.get('X-API-Key')
    print(f"Received API Key: {api_key}")
    print(f"Expected API Key: {API_KEY}")
    print(f"Environment NEXT_PUBLIC_API_KEY: {os.getenv('NEXT_PUBLIC_API_KEY')}")
    
    if not api_key or api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    return None

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """音声ファイル処理のメインエンドポイント（新しいアーキテクチャ）"""
    global processing_status
    
    try:
        # 既に処理中の場合はエラーを返す
        if processing_status["is_processing"]:
            return jsonify({"error": "既に処理が実行中です"}), 409
        
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
            return auth_error
        
        # ファイルアップロードを取得
        if 'audioFile' not in request.files:
            processing_status["is_processing"] = False
            processing_status["error"] = "audioFile is required"
            return jsonify({"error": "audioFile is required"}), 400
        
        audio_file = request.files['audioFile']
        title = request.form.get('title', 'Untitled')
        
        if audio_file.filename == '':
            processing_status["is_processing"] = False
            processing_status["error"] = "No file selected"
            return jsonify({"error": "No file selected"}), 400
        
        # ファイルサイズをチェック
        audio_file.seek(0, 2)  # ファイルの末尾に移動
        file_size = audio_file.tell()
        audio_file.seek(0)  # ファイルの先頭に戻す
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            processing_status["is_processing"] = False
            processing_status["error"] = "File too large"
            return jsonify({"error": "File too large. Maximum size is 100MB"}), 413
        
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
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存中...")
            audio_path = os.path.join(temp_dir, "audio.mp3")
            audio_file.save(audio_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存完了")
            
            # 新しいアーキテクチャで講義処理を実行
            processing_status["current_step"] = "講義処理実行中..."
            processing_status["progress"] = 20
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 講義処理実行中...")
            
            # 講義処理サービスを使用
            result = lecture_service.process_lecture(
                audio_file_path=audio_path,
                title=title,
                domain="general"
            )
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 講義処理完了")
            
            # 結果を返す
            processing_status["current_step"] = "処理完了"
            processing_status["progress"] = 100
            
            response = {
                "title": title,
                "audioFileName": audio_file.filename,
                "audioDuration": result.audio_duration,
                "segmentCount": len(result.transcription.segments),
                "firstDraft": result.transcription.text,
                "transcript": result.enhanced_text,
                "technicalTerms": result.technical_terms,
                "status": "completed",
                "architecture": "new"
            }
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 処理完了 - 結果を返送中")
            
            # 処理状況をリセット
            processing_status["is_processing"] = False
            processing_status["current_step"] = ""
            processing_status["progress"] = 0
            
            return jsonify(response)
            
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] エラー: {str(e)}")
        import traceback
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] スタックトレース: {traceback.format_exc()}")
        
        # エラー時に処理状況をリセット
        processing_status["is_processing"] = False
        processing_status["error"] = str(e)
        processing_status["current_step"] = ""
        processing_status["progress"] = 0
        
        return jsonify({"error": f"処理中にエラーが発生しました: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
