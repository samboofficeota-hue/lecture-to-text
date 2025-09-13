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

    const response = await fetch(`${CLOUD_RUN_API_URL}/process-audio`, {
      method: "POST",
      body: cloudRunFormData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Cloud Run API エラー:", errorData);
      return NextResponse.json(
        { error: `Cloud Run APIエラー: ${errorData.error || response.statusText}` },
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
