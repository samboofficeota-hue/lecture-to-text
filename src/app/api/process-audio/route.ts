import { NextRequest, NextResponse } from "next/server";

const CLOUD_RUN_API_URL = process.env.CLOUD_RUN_API_URL || "https://lecture-to-text-api-1088729528504.asia-northeast1.run.app";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audioFile = formData.get("audioFile") as File;
    const title = formData.get("title") as string;

    if (!audioFile) {
      return NextResponse.json(
        { error: "音声ファイルが指定されていません" },
        { status: 400 }
      );
    }

    // ファイルサイズ制限（100MB）
    if (audioFile.size > 100 * 1024 * 1024) {
      return NextResponse.json(
        { error: "ファイルサイズが大きすぎます。100MB以下にしてください。" },
        { status: 400 }
      );
    }

    // ファイル形式チェック
    if (!audioFile.type.includes('audio/mpeg') && !audioFile.name.toLowerCase().endsWith('.mp3')) {
      return NextResponse.json(
        { error: "MP3音声ファイルを選択してください" },
        { status: 400 }
      );
    }

    console.log(`Cloud Run APIにリクエスト送信中: ${audioFile.name}`);
    
    // Cloud Run APIにファイルを転送
    const cloudRunFormData = new FormData();
    cloudRunFormData.append("audioFile", audioFile);
    cloudRunFormData.append("title", title || "講義音声");

    // リトライ機能付きでCloud Run APIを呼び出し
    let response;
    let lastError;
    const maxRetries = 3;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`試行 ${attempt}/${maxRetries}: Cloud Run APIにリクエスト送信中`);
        
        response = await fetch(`${CLOUD_RUN_API_URL}/process-audio`, {
          method: "POST",
          body: cloudRunFormData,
          headers: {
            'User-Agent': 'Vercel-API-Route/1.0'
          }
        });
        
        // 成功した場合はループを抜ける
        if (response.ok) {
          break;
        }
        
        // 503 Service Unavailableの場合はリトライ
        if (response.status === 503 && attempt < maxRetries) {
          console.log(`Service Unavailable (503) - ${attempt + 1}回目のリトライを${attempt * 2}秒後に実行`);
          await new Promise(resolve => setTimeout(resolve, attempt * 2000));
          continue;
        }
        
        // その他のエラーまたは最後の試行の場合はループを抜ける
        break;
        
      } catch (error) {
        lastError = error;
        console.error(`試行 ${attempt} でエラー:`, error);
        
        if (attempt < maxRetries) {
          console.log(`${attempt * 2}秒後にリトライします`);
          await new Promise(resolve => setTimeout(resolve, attempt * 2000));
        }
      }
    }
    
    // すべての試行が失敗した場合
    if (!response) {
      throw lastError || new Error('Cloud Run APIへの接続に失敗しました');
    }

    if (!response.ok) {
      let errorMessage = response.statusText;
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || response.statusText;
        console.error("Cloud Run API エラー:", errorData);
      } catch {
        // JSON解析に失敗した場合、レスポンステキストをそのまま使用
        const responseText = await response.text();
        errorMessage = responseText || response.statusText;
        console.error("Cloud Run API エラー (JSON解析失敗):", responseText);
      }
      
      return NextResponse.json(
        { error: `Cloud Run APIエラー: ${errorMessage}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Vercel API Route Error:", error);
    return NextResponse.json(
      { error: `Vercel APIルートでエラーが発生しました: ${(error as Error).message}` },
      { status: 500 }
    );
  }
}
