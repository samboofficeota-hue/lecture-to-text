import { NextRequest, NextResponse } from "next/server";

const CLOUD_RUN_API_URL = "https://lecture-to-text-api-1088729528504.asia-northeast1.run.app";

export async function POST(request: NextRequest) {
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

    console.log(`Cloud Run APIにリクエスト送信中: ${videoUrl}`);

    // Cloud Run APIにリクエストを転送
    const response = await fetch(`${CLOUD_RUN_API_URL}/process-video`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        videoUrl,
        title: title || "Untitled",
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Cloud Run API エラー:", errorText);
      return NextResponse.json(
        { error: `動画処理に失敗しました: ${errorText}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    console.log("Cloud Run API からの応答を受信");

    return NextResponse.json(result);

  } catch (error) {
    console.error("エラー:", error);
    return NextResponse.json(
      { error: `処理中にエラーが発生しました: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
}

function isValidVideoUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    
    // YouTube URL
    if (urlObj.hostname.includes("youtube.com") || urlObj.hostname.includes("youtu.be")) {
      return true;
    }
    
    // ZOOM URL
    if (urlObj.hostname.includes("zoom.us")) {
      return true;
    }
    
    return false;
  } catch {
    return false;
  }
}