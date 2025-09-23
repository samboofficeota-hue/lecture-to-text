"use client";

import React, { useState } from "react";

export default function Home() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoTitle, setVideoTitle] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setVideoFile(file || null);
    setResult(null);
  };

  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setVideoTitle(event.target.value);
  };

  const handleProcess = async () => {
    if (!videoFile) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('audioFile', videoFile);
      formData.append('title', videoTitle || '講義音声');

      const CLOUD_RUN_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://darwin-lecture-api-1088729528504.asia-northeast1.run.app";
      const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'test-api-key-12345';

      console.log("Production API upload:", CLOUD_RUN_API_URL);
      console.log("API Key:", API_KEY ? `${API_KEY.substring(0, 10)}...` : 'NOT SET');

      const response = await fetch(`${CLOUD_RUN_API_URL}/process-audio`, {
        method: "POST",
        body: formData,
        headers: {
          'User-Agent': 'Vercel-Client/1.0',
          'X-API-Key': API_KEY
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      setResult(data.transcript || "処理が完了しました。");
    } catch (error) {
      console.error("API Error:", error);
      setResult(`エラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const isValidAudioFile = (file: File): boolean => {
    return file.type === 'audio/mpeg' || file.type === 'audio/mp3' || file.name.toLowerCase().endsWith('.mp3');
  };

  return (
    <div className="min-h-screen gradient-bg px-4 py-6 sm:px-8 sm:py-8">
      <div className="max-w-4xl mx-auto">
        {/* ヘッダー */}
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
            講義音声から教材自動生成
          </h1>
          <p className="text-base sm:text-lg lg:text-xl text-gray-600">
            MP3音声ファイルから、講義録や教材を自動で生成しましょう
          </p>
        </div>

        {/* メインコンテンツ */}
        <div className="bg-white rounded-lg card-shadow p-4 sm:p-6 lg:p-8 mb-6 sm:mb-8">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4 sm:mb-6">
            講義録生成
          </h2>

          <div className="flex flex-col gap-4 sm:gap-6">
            {/* ファイルアップロード */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                MP3音声ファイル
              </label>
              <input
                type="file"
                id="audioFile"
                accept=".mp3,audio/mpeg"
                onChange={handleFileChange}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isProcessing}
              />
              {videoFile && !isValidAudioFile(videoFile) && (
                <p className="mt-1 text-sm text-red-600">
                  MP3音声ファイルを選択してください
                </p>
              )}
              {videoFile && (
                <p className="mt-1 text-sm text-green-600">
                  選択されたファイル: {videoFile.name} ({(videoFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>

            {/* タイトル入力 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                講義タイトル（任意）
              </label>
              <input
                type="text"
                id="videoTitle"
                value={videoTitle}
                onChange={handleTitleChange}
                placeholder="例: 2024年度新入社員研修 - 第1回"
                className="w-full px-3 py-3 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isProcessing}
              />
            </div>

            {/* 処理ボタン */}
            <div className="text-center">
              <button
                onClick={handleProcess}
                disabled={!videoFile || !isValidAudioFile(videoFile) || isProcessing}
                className={`px-8 py-3 rounded-lg font-medium text-base border-0 ${
                  isProcessing 
                    ? 'bg-gray-400 text-white cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer'
                } disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200`}
              >
                {isProcessing ? "処理中..." : "講義録を生成"}
              </button>
            </div>
          </div>
        </div>

        {/* 結果表示 */}
        {result && (
          <div className="bg-white rounded-lg card-shadow p-4 sm:p-6 lg:p-8">
            <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">
              生成結果
            </h3>
            <div className="bg-gray-50 rounded-lg p-3 sm:p-4 max-h-80 sm:max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-xs sm:text-sm text-gray-700 m-0 font-mono">
                {result}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}