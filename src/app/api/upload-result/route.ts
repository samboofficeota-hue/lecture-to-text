import { NextRequest, NextResponse } from "next/server";
import { put } from "@vercel/blob";

export async function POST(request: NextRequest) {
  try {
    const { filename, content, contentType = "text/plain" } = await request.json();

    if (!filename || !content) {
      return NextResponse.json(
        { error: "ファイル名とコンテンツが必要です" },
        { status: 400 }
      );
    }

    // Vercel Blob Storageに保存
    const blob = await put(filename, content, {
      access: 'public',
      contentType: contentType,
    });

    return NextResponse.json({
      success: true,
      url: blob.url,
      filename: filename,
    });

  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json(
      { error: "ファイルのアップロードに失敗しました" },
      { status: 500 }
    );
  }
}
