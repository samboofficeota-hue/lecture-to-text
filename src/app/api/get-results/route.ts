import { NextRequest, NextResponse } from "next/server";
import { list } from "@vercel/blob";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const prefix = searchParams.get('prefix') || 'lecture-';

    // Vercel Blob Storageからファイル一覧を取得
    const { blobs } = await list({
      prefix: prefix,
      limit: 100,
    });

    // 講義録関連のファイルのみをフィルタリング
    const lectureFiles = blobs
      .filter(blob => 
        blob.pathname.includes('first-draft') || 
        blob.pathname.includes('final-transcript') ||
        blob.pathname.includes('summary') ||
        blob.pathname.includes('materials')
      )
      .map(blob => ({
        filename: blob.pathname,
        url: blob.url,
        size: blob.size,
        uploadedAt: blob.uploadedAt,
        type: getFileType(blob.pathname),
      }))
      .sort((a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime());

    return NextResponse.json({
      success: true,
      files: lectureFiles,
    });

  } catch (error) {
    console.error("Get results error:", error);
    return NextResponse.json(
      { error: "ファイル一覧の取得に失敗しました" },
      { status: 500 }
    );
  }
}

function getFileType(filename: string): string {
  if (filename.includes('first-draft')) return 'first-draft';
  if (filename.includes('final-transcript')) return 'final-transcript';
  if (filename.includes('summary')) return 'summary';
  if (filename.includes('materials')) return 'materials';
  return 'unknown';
}
