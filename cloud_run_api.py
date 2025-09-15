"""
Cloud Run用の音声処理APIサーバー
GitHub Actions自動デプロイテスト用のコメント追加（トリガーテスト）
"""
import os
import json
import tempfile
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
# yt_dlpは不要になったため削除
from faster_whisper import WhisperModel
import openai
from text_enhancer import TextEnhancer
import config
import hashlib
import hmac
import time

app = Flask(__name__)

# セキュリティ強化: 特定のOriginのみ許可
CORS(app, origins=[
    "https://lecture-to-text-qov0p5jjn-yoshis-projects-421cbceb.vercel.app",
    "https://lecture-to-text.vercel.app",
    "https://lecture-to-text-omega.vercel.app",  # 新しいVercelプロジェクト
    "https://lecture-to-text-7xtgo3bbl-yoshis-projects-421cbceb.vercel.app",  # 最新のVercelプロジェクト
    "http://localhost:3000"  # 開発用
])

# APIキー設定
API_KEY = os.getenv('API_KEY', 'default-secret-key-change-this')

# ファイルアップロードサイズ制限を設定（100MB）
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

@app.errorhandler(413)
def too_large(e):
    """ファイルサイズが大きすぎる場合のエラーハンドラー"""
    return jsonify({"error": "File too large. Maximum size is 100MB"}), 413

# Whisperモデルの初期化（グローバル変数として）
whisper_model = None

# 処理状況を追跡するためのグローバル変数
processing_status = {
    "is_processing": False,
    "current_step": "",
    "progress": 0,
    "total_steps": 0,
    "start_time": None,
    "error": None
}

def init_whisper():
    """Whisperモデルを初期化"""
    global whisper_model
    if whisper_model is None:
        print("Whisperモデルを初期化中...")
        whisper_model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        print("Whisperモデル初期化完了")

# 動画ダウンロード機能は削除（音声ファイルアップロードに変更）

# 動画関連の関数は削除（音声ファイル処理に変更）

def get_audio_duration(audio_path):
    """音声の長さを取得"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

# 動画セグメント分割機能は削除（音声ファイル処理に変更）

def create_audio_segments(audio_path, segment_duration=180):  # 3分 = 180秒
    """音声をセグメントに分割"""
    duration = get_audio_duration(audio_path)
    segments = []
    
    for start_time in range(0, int(duration), segment_duration):
        end_time = min(start_time + segment_duration, duration)
        segments.append({
            'start': start_time,
            'end': end_time,
            'duration': end_time - start_time
        })
    
    return segments

def extract_audio_segment(audio_path, start_time, duration, output_path):
    """音声からセグメントを抽出"""
    cmd = [
        'ffmpeg', '-i', audio_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-acodec', 'pcm_s16le',
        '-ar', '16000',  # Whisper推奨サンプルレート
        '-ac', '1',      # モノラル
        '-y', output_path
    ]
    subprocess.run(cmd, check=True)

def transcribe_audio(audio_path):
    """音声を文字起こし"""
    segments, info = whisper_model.transcribe(audio_path, beam_size=1, best_of=1)
    
    transcript_parts = []
    for segment in segments:
        transcript_parts.append(f"[{segment.start:.1f}s-{segment.end:.1f}s] {segment.text}")
    
    return "\n".join(transcript_parts)

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({"status": "healthy"})

@app.route('/status', methods=['GET'])
def get_processing_status():
    """処理状況を取得"""
    global processing_status
    return jsonify(processing_status)

def verify_api_key():
    """APIキーを検証"""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    return None

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """音声ファイル処理のメインエンドポイント"""
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
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声処理開始: {title}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ファイル名: {audio_file.filename}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ファイルサイズ: {file_size / 1024 / 1024:.2f} MB")
        
        # Whisperモデルを初期化
        processing_status["current_step"] = "Whisperモデル初期化中..."
        processing_status["progress"] = 5
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Whisperモデル初期化中...")
        init_whisper()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Whisperモデル初期化完了")
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            # 音声ファイルを保存
            processing_status["current_step"] = "音声ファイル保存中..."
            processing_status["progress"] = 10
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存中...")
            audio_path = os.path.join(temp_dir, "audio.mp3")
            audio_file.save(audio_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声ファイル保存完了")
            
            # 音声の長さを取得
            processing_status["current_step"] = "音声の長さを取得中..."
            processing_status["progress"] = 15
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声の長さを取得中...")
            duration = get_audio_duration(audio_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声の長さ: {duration:.1f}秒")
            
            # セグメントに分割
            processing_status["current_step"] = "音声をセグメントに分割中..."
            processing_status["progress"] = 20
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 音声をセグメントに分割中...")
            segments = create_audio_segments(audio_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] セグメント数: {len(segments)}")
            
            # 各セグメントを処理
            all_transcripts = []
            total_segments = len(segments)
            processing_status["total_steps"] = total_segments + 2  # セグメント処理 + 文字起こし結合 + ChatGPT処理
            
            for i, segment in enumerate(segments):
                processing_status["current_step"] = f"セグメント {i+1}/{total_segments} 処理中..."
                processing_status["progress"] = 25 + (i * 60 // total_segments)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] セグメント {i+1}/{total_segments} 処理開始...")
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] セグメント時間: {segment['start']:.1f}s - {segment['end']:.1f}s")
                
                segment_audio_path = os.path.join(temp_dir, f"segment_{i}.wav")
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] セグメント音声抽出中...")
                extract_audio_segment(
                    audio_path, 
                    segment['start'], 
                    segment['duration'], 
                    segment_audio_path
                )
                
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Whisper文字起こし実行中...")
                transcript = transcribe_audio(segment_audio_path)
                all_transcripts.append(transcript)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] セグメント {i+1}/{total_segments} 完了")
            
            # 全セグメントの文字起こしを結合
            processing_status["current_step"] = "文字起こし結果を結合中..."
            processing_status["progress"] = 85
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 文字起こし結果を結合中...")
            first_draft = "\n\n".join(all_transcripts)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 文字起こし完了 (文字数: {len(first_draft)})")
            
            # ChatGPTでテキストを強化
            processing_status["current_step"] = "ChatGPTでテキスト強化中..."
            processing_status["progress"] = 90
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ChatGPTでテキスト強化開始...")
            enhancer = TextEnhancer()
            enhanced_result = enhancer.process_full_pipeline(first_draft)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ChatGPTテキスト強化完了")
            
            # 結果を返す
            processing_status["current_step"] = "処理完了"
            processing_status["progress"] = 100
            result = {
                "title": title,
                "audioFileName": audio_file.filename,
                "audioDuration": duration,
                "segmentCount": len(segments),
                "firstDraft": first_draft,
                "transcript": enhanced_result.get('enhanced_text', first_draft),
                "technicalTerms": enhanced_result.get('technical_terms', []),
                "status": "completed"
            }
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 処理完了 - 結果を返送中")
            
            # 処理状況をリセット
            processing_status["is_processing"] = False
            processing_status["current_step"] = ""
            processing_status["progress"] = 0
            
            return jsonify(result)
            
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
# Test with new service account key
