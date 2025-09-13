import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { unlink } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";
import youtubedl from "youtube-dl-exec";

export async function POST(request: NextRequest) {
  let tempVideoPath: string | null = null;
  
  try {
    const { videoUrl, title } = await request.json();

    if (!videoUrl) {
      return NextResponse.json(
        { error: "動画URLが指定されていません" },
        { status: 400 }
      );
    }

    // URL検証
    if (!isValidVideoUrl(videoUrl)) {
      return NextResponse.json(
        { error: "サポートされていない動画URLです。ZOOM録画またはYouTubeのURLを入力してください。" },
        { status: 400 }
      );
    }

    // 一時ファイルパスを生成
    tempVideoPath = join(tmpdir(), `video_${Date.now()}.mp4`);

    // 動画をダウンロード
    console.log("動画をダウンロード中...");
    await downloadVideo(videoUrl, tempVideoPath);

    // 動画の長さを取得
    const videoDuration = await getVideoDuration(tempVideoPath);
    console.log(`動画の長さ: ${videoDuration}秒`);

    // 動画をセグメントに分割
    const segments = createVideoSegments(videoDuration);
    console.log(`${segments.length}個のセグメントに分割`);

    // 処理時間の推測
    const estimatedProcessingTime = estimateProcessingTime(videoDuration, segments.length);
    console.log(`推定処理時間: ${estimatedProcessingTime}分`);

    const allTranscripts: string[] = [];

    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i];
      console.log(`セグメント ${i + 1}/${segments.length} を処理中: ${segment.startTime}s - ${segment.endTime}s`);

      // セグメントの音声を抽出
      const segmentAudioPath = await extractAudioSegment(tempVideoPath, segment.startTime, segment.endTime);

      // セグメントを文字起こし
      const segmentTranscript = await transcribeAudio(segmentAudioPath);
      allTranscripts.push(`[${formatTime(segment.startTime)} - ${formatTime(segment.endTime)}]\n${segmentTranscript}`);

      // 一時ファイルを削除
      try { await unlink(segmentAudioPath); } catch {}

      // 進捗を更新（実際の実装ではWebSocketやServer-Sent Eventsを使用）
      console.log(`セグメント ${i + 1} 完了`);
    }

    // 全セグメントの文字起こしを結合
    const firstDraft = allTranscripts.join('\n\n');

    // ChatGPTで文章を改善
    console.log("ChatGPTで文章を改善中...");
    const enhancedTranscript = await enhanceWithChatGPT(firstDraft, videoDuration, segments.length);

    return NextResponse.json({
      success: true,
      transcript: enhancedTranscript,
      firstDraft: firstDraft,
      videoUrl: videoUrl,
      title: title || "講義動画",
      videoDuration: videoDuration,
      segmentCount: segments.length,
      estimatedProcessingTime: estimatedProcessingTime,
    });

  } catch (error) {
    console.error("Video processing error:", error);
    return NextResponse.json(
      { error: `処理中にエラーが発生しました: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  } finally {
    // 一時ファイルの削除
    if (tempVideoPath) {
      try { await unlink(tempVideoPath); } catch {}
    }
  }
}

// URL検証関数
function isValidVideoUrl(url: string): boolean {
  try {
    // const urlObj = new URL(url);
    return (
      url.includes('zoom.us') || 
      url.includes('youtube.com') || 
      url.includes('youtu.be')
    );
  } catch {
    return false;
  }
}

// 動画ダウンロード関数
async function downloadVideo(videoUrl: string, outputPath: string): Promise<void> {
  try {
    console.log(`Downloading video from: ${videoUrl}`);
    
    const options: {
      output: string;
      format: string;
      noPlaylist: boolean;
      userAgent?: string;
    } = {
      output: outputPath,
      format: 'best[height<=720]',
      noPlaylist: true,
    };

    if (videoUrl.includes('zoom.us')) {
      // ZOOM録画の場合
      options.userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36";
    }

    await youtubedl(videoUrl, options);
    console.log('Video download completed successfully');
  } catch (error) {
    console.error('Video download error:', error);
    throw new Error(`動画ダウンロードに失敗しました: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// 動画の長さを取得する関数
async function getVideoDuration(videoPath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const process = spawn('ffprobe', [
      '-v', 'quiet',
      '-show_entries', 'format=duration',
      '-of', 'csv=p=0',
      videoPath
    ]);

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        const duration = parseFloat(stdout.trim());
        resolve(duration);
      } else {
        console.error("ffprobe stderr:", stderr);
        reject(new Error(`動画の長さ取得に失敗しました (コード: ${code})`));
      }
    });
  });
}

// 動画セグメントを作成する関数
function createVideoSegments(duration: number): Array<{startTime: number, endTime: number}> {
  const segmentLength = 360; // 6分 = 360秒
  const segments: Array<{startTime: number, endTime: number}> = [];

  for (let start = 0; start < duration; start += segmentLength) {
    const end = Math.min(start + segmentLength, duration);
    segments.push({ startTime: start, endTime: end });
  }

  return segments;
}

// 処理時間を推測する関数
function estimateProcessingTime(videoDuration: number, segmentCount: number): number {
  // 各セグメントの処理時間を推測（秒）
  const segmentProcessingTime = 20; // 6分のセグメントあたり約20秒
  const whisperProcessingTime = 20; // Whisper処理時間
  const chatgptProcessingTime = 10; // ChatGPT処理時間
  
  // 総処理時間（秒）
  const totalProcessingTime = (segmentProcessingTime + whisperProcessingTime + chatgptProcessingTime) * segmentCount;
  
  // 分に変換して返す
  return Math.ceil(totalProcessingTime / 60);
}

// 音声セグメントを抽出する関数
async function extractAudioSegment(videoPath: string, startTime: number, endTime: number): Promise<string> {
  return new Promise((resolve, reject) => {
    const outputPath = join(tmpdir(), `audio_${Date.now()}_${startTime}_${endTime}.wav`);
    
    const process = spawn('ffmpeg', [
      '-i', videoPath,
      '-ss', startTime.toString(),
      '-t', (endTime - startTime).toString(),
      '-acodec', 'pcm_s16le',
      '-ar', '16000',
      '-ac', '1',
      '-y',
      outputPath
    ]);

    let stderr = '';

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve(outputPath);
      } else {
        console.error("ffmpeg stderr:", stderr);
        reject(new Error(`音声抽出に失敗しました (コード: ${code})`));
      }
    });
  });
}

// 音声を文字起こしする関数
async function transcribeAudio(audioPath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [
      '-c', `
import sys
sys.path.append('/tmp')
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe("${audioPath}")
result = " ".join([segment.text for segment in segments])
print(result)
      `
    ]);

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        console.error("Whisper stderr:", stderr);
        reject(new Error(`文字起こしに失敗しました (コード: ${code})`));
      }
    });
  });
}

// ChatGPTで文章を改善する関数
async function enhanceWithChatGPT(text: string, videoDuration: number, segmentCount: number): Promise<string> {
  const openaiApiKey = process.env.OPENAI_API_KEY;
  
  if (!openaiApiKey) {
    console.warn("OpenAI API key not found, returning original text");
    return text;
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `あなたは講義録の編集専門家です。以下の文字起こしテキストを、読みやすい講義録に改善してください。

動画情報:
- 動画の長さ: ${Math.floor(videoDuration / 60)}分${videoDuration % 60}秒
- セグメント数: ${segmentCount}個

改善のポイント:
1. 固有名詞や専門用語の正確性を向上
2. 文章の流れを自然に
3. 段落分けを適切に
4. 誤字脱字の修正
5. 講義の構造を明確に

元のテキストの内容は保持しつつ、読みやすさを向上させてください。`
          },
          {
            role: 'user',
            content: text
          }
        ],
        max_tokens: 4000,
        temperature: 0.3,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('ChatGPT enhancement error:', error);
    return text; // エラーの場合は元のテキストを返す
  }
}

// 時間をフォーマットする関数
function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}