"""
Cloud Run用の音声処理APIサーバー
自動デプロイテスト用のコメント追加
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

app = Flask(__name__)
CORS(app)

# Whisperモデルの初期化（グローバル変数として）
whisper_model = None

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

@app.route('/process-audio', methods=['POST'])
def process_audio():
    """音声ファイル処理のメインエンドポイント"""
    try:
        # ファイルアップロードを取得
        if 'audioFile' not in request.files:
            return jsonify({"error": "audioFile is required"}), 400
        
        audio_file = request.files['audioFile']
        title = request.form.get('title', 'Untitled')
        
        if audio_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        print(f"音声処理開始: {title}")
        print(f"ファイル名: {audio_file.filename}")
        
        # Whisperモデルを初期化
        init_whisper()
        
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            # 音声ファイルを保存
            audio_path = os.path.join(temp_dir, "audio.mp3")
            audio_file.save(audio_path)
            
            # 音声の長さを取得
            duration = get_audio_duration(audio_path)
            print(f"音声の長さ: {duration:.1f}秒")
            
            # セグメントに分割
            segments = create_audio_segments(audio_path)
            print(f"セグメント数: {len(segments)}")
            
            # 各セグメントを処理
            all_transcripts = []
            for i, segment in enumerate(segments):
                print(f"セグメント {i+1}/{len(segments)} 処理中...")
                
                segment_audio_path = os.path.join(temp_dir, f"segment_{i}.wav")
                extract_audio_segment(
                    audio_path, 
                    segment['start'], 
                    segment['duration'], 
                    segment_audio_path
                )
                
                transcript = transcribe_audio(segment_audio_path)
                all_transcripts.append(transcript)
            
            # 全セグメントの文字起こしを結合
            first_draft = "\n\n".join(all_transcripts)
            print("文字起こし完了")
            
            # ChatGPTでテキストを強化
            print("ChatGPTでテキスト強化中...")
            enhancer = TextEnhancer()
            enhanced_result = enhancer.process_full_pipeline(first_draft)
            
            # 結果を返す
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
            
            print("処理完了")
            return jsonify(result)
            
    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({"error": f"処理中にエラーが発生しました: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
# Test with new service account key
