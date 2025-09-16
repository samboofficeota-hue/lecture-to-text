"use client";

import { useState } from "react";

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
      formData.append('audio_file', videoFile);
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
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%)', 
      padding: '2rem' 
    }}>
      <div style={{ maxWidth: '56rem', margin: '0 auto' }}>
        {/* ヘッダー */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ 
            fontSize: '2.25rem', 
            fontWeight: 'bold', 
            color: '#111827', 
            marginBottom: '1rem' 
          }}>
            講義音声から教材自動生成
          </h1>
          <p style={{ fontSize: '1.25rem', color: '#4b5563' }}>
            MP3音声ファイルから、講義録や教材を自動で生成しましょう
          </p>
        </div>

        {/* メインコンテンツ */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '0.5rem', 
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', 
          padding: '2rem', 
          marginBottom: '2rem' 
        }}>
          <h2 style={{ 
            fontSize: '1.25rem', 
            fontWeight: '600', 
            color: '#111827', 
            marginBottom: '1.5rem' 
          }}>
            講義録生成
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* ファイルアップロード */}
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '0.875rem', 
                fontWeight: '500', 
                color: '#374151', 
                marginBottom: '0.5rem' 
              }}>
                MP3音声ファイル
              </label>
              <input
                type="file"
                id="audioFile"
                accept=".mp3,audio/mpeg"
                onChange={handleFileChange}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#111827',
                  backgroundColor: 'white'
                }}
                disabled={isProcessing}
              />
              {videoFile && !isValidAudioFile(videoFile) && (
                <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#dc2626' }}>
                  MP3音声ファイルを選択してください
                </p>
              )}
              {videoFile && (
                <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#059669' }}>
                  選択されたファイル: {videoFile.name} ({(videoFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>

            {/* タイトル入力 */}
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '0.875rem', 
                fontWeight: '500', 
                color: '#374151', 
                marginBottom: '0.5rem' 
              }}>
                講義タイトル（任意）
              </label>
              <input
                type="text"
                id="videoTitle"
                value={videoTitle}
                onChange={handleTitleChange}
                placeholder="例: 2024年度新入社員研修 - 第1回"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#111827',
                  backgroundColor: 'white'
                }}
                disabled={isProcessing}
              />
            </div>

            {/* 処理ボタン */}
            <div style={{ textAlign: 'center' }}>
              <button
                onClick={handleProcess}
                disabled={!videoFile || !isValidAudioFile(videoFile) || isProcessing}
                style={{
                  backgroundColor: isProcessing ? '#9ca3af' : '#2563eb',
                  color: 'white',
                  fontWeight: '500',
                  padding: '0.75rem 2rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  fontSize: '1rem'
                }}
              >
                {isProcessing ? "処理中..." : "講義録を生成"}
              </button>
            </div>
          </div>
        </div>

        {/* 結果表示 */}
        {result && (
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '0.5rem', 
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', 
            padding: '2rem' 
          }}>
            <h3 style={{ 
              fontSize: '1.125rem', 
              fontWeight: '600', 
              color: '#111827', 
              marginBottom: '1rem' 
            }}>
              生成結果
            </h3>
            <div style={{ 
              backgroundColor: '#f9fafb', 
              borderRadius: '0.5rem', 
              padding: '1rem', 
              maxHeight: '24rem', 
              overflowY: 'auto' 
            }}>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                fontSize: '0.875rem', 
                color: '#374151',
                margin: 0
              }}>
                {result}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}