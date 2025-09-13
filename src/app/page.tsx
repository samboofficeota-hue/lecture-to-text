"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoTitle, setVideoTitle] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  // const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [result, setResult] = useState<string | null>(null);
  const [estimatedTime, setEstimatedTime] = useState<number | null>(null);
  const [remainingTime, setRemainingTime] = useState<number | null>(null);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [videoInfo, setVideoInfo] = useState<{
    duration: number;
    segmentCount: number;
  } | null>(null);
  
  // プロセスステップの状態管理
  // const [currentProcessStep, setCurrentProcessStep] = useState<number>(0);
  const [processSteps, setProcessSteps] = useState<Array<{
    id: number;
    title: string;
    status: "pending" | "in_progress" | "completed";
    result: string | null;
  }>>([
    { id: 1, title: "MP3音声ファイルをアップロードする", status: "pending", result: null },
    { id: 2, title: "AI文字起こし処理中...", status: "pending", result: null },
    { id: 3, title: "講義録を生成中...", status: "pending", result: null },
  ]);

  // 講義録一覧の状態管理（簡略化）
  const [lectureRecords, setLectureRecords] = useState<Array<{
    id: string;
    title: string;
    finalTranscript: string;
    createdAt: string;
    audioDuration: number;
  }>>([]);
  
  const [showRecords, setShowRecords] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setVideoFile(file || null);
    setResult(null);
    if (file) {
      updateProcessStep(1, "completed");
    } else {
      resetProcessSteps();
      stopCountdown();
    }
  };

  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setVideoTitle(event.target.value);
  };

  const handleProcess = async () => {
    if (!videoFile) {
      alert("音声ファイルを選択してください");
      return;
    }

    setIsProcessing(true);
    // setUploadProgress(0);
    setCurrentStep("音声ファイルをアップロード中...");
    setEstimatedTime(null);
    setVideoInfo(null);
    
    // ステップ1を完了としてマーク
    updateProcessStep(1, "completed");
    updateProcessStep(2, "in_progress");

    try {
      // 進捗をシミュレート（実際の実装ではWebSocketでリアルタイム更新）
      const progressSteps = [
        { step: "音声ファイルをアップロード中...", progress: 10 },
        { step: "音声の長さを確認中...", progress: 20 },
        { step: "音声を3分ずつに分割中...", progress: 30 },
        { step: "第1セグメントを処理中...", progress: 50 },
        { step: "第2セグメントを処理中...", progress: 65 },
        { step: "第3セグメントを処理中...", progress: 80 },
        { step: "AI文字起こし処理中...", progress: 85 },
        { step: "文章を改善中...", progress: 90 },
        { step: "講義録を生成中...", progress: 95 },
      ];

      let currentStepIndex = 0;
      const progressInterval = setInterval(() => {
        if (currentStepIndex < progressSteps.length) {
          setCurrentStep(progressSteps[currentStepIndex].step);
          // setUploadProgress(progressSteps[currentStepIndex].progress);
          currentStepIndex++;
        }
      }, 3000);

      const formData = new FormData();
      formData.append("audioFile", videoFile);
      formData.append("title", videoTitle.trim() || "講義音声");

      // Vercelの制限を回避するため、直接Cloud Runにアップロード
      const CLOUD_RUN_API_URL = "https://lecture-to-text-api-1088729528504.asia-northeast1.run.app";
      
      const response = await fetch(`${CLOUD_RUN_API_URL}/process-audio`, {
        method: "POST",
        body: formData,
        headers: {
          'User-Agent': 'Vercel-Client/1.0'
        }
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("API Error:", errorData);
        throw new Error(errorData.error || "処理に失敗しました");
      }

      setCurrentStep("完了！");
      // setUploadProgress(100);
      const data = await response.json();
      setResult(data.transcript);
      
      // 音声情報を保存
      if (data.audioDuration && data.segmentCount) {
        setVideoInfo({
          duration: data.audioDuration,
          segmentCount: data.segmentCount
        });
      }
      if (data.estimatedProcessingTime) {
        setEstimatedTime(data.estimatedProcessingTime);
        // カウントダウンタイマーを開始（分を秒に変換）
        startCountdown(data.estimatedProcessingTime * 60);
      }
      
      // ステップ2と3を完了としてマーク
      updateProcessStep(2, "completed");
      updateProcessStep(3, "completed", data.transcript);
      
      // 講義録を保存
      saveLectureRecord(data);
      
      // カウントダウンタイマーを停止
      stopCountdown();
    } catch (error) {
      console.error("Error:", error);
      alert("エラーが発生しました: " + (error as Error).message);
      stopCountdown();
    } finally {
      setIsProcessing(false);
      // setUploadProgress(0);
      setCurrentStep("");
    }
  };

  const isValidAudioFile = (file: File) => {
    return file.type === 'audio/mpeg' || file.type === 'audio/mp3' || file.name.toLowerCase().endsWith('.mp3');
  };

  // プロセスステップを更新する関数
  const updateProcessStep = (stepId: number, status: "pending" | "in_progress" | "completed", result?: string) => {
    setProcessSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, result: result || step.result }
        : step
    ));
  };

  // プロセスステップをリセットする関数
  const resetProcessSteps = () => {
    setProcessSteps(prev => prev.map(step => ({ ...step, status: "pending", result: null })));
    // setCurrentProcessStep(0);
  };

  // 時間をフォーマットする関数（分:秒）
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // カウントダウンタイマーを開始する関数
  const startCountdown = (totalSeconds: number) => {
    setRemainingTime(totalSeconds);
    setStartTime(Date.now());
  };

  // カウントダウンタイマーを停止する関数
  const stopCountdown = () => {
    setRemainingTime(null);
    setStartTime(null);
  };

  // 講義録を保存する関数（簡略化）
  const saveLectureRecord = (data: { title: string; transcript: string; audioDuration?: number }) => {
    const newRecord = {
      id: Date.now().toString(),
      title: data.title || "講義音声",
      finalTranscript: data.transcript || "",
      createdAt: new Date().toLocaleString('ja-JP'),
      audioDuration: data.audioDuration || 0,
    };
    
    setLectureRecords(prev => [newRecord, ...prev]);
  };

  // 講義録を削除する関数
  const deleteLectureRecord = (id: string) => {
    setLectureRecords(prev => prev.filter(record => record.id !== id));
  };

  // カウントダウンタイマーの効果
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (remainingTime !== null && startTime !== null && remainingTime > 0) {
      interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const newRemainingTime = Math.max(0, remainingTime - elapsed);
        
        if (newRemainingTime <= 0) {
          setRemainingTime(0);
          clearInterval(interval);
        } else {
          setRemainingTime(newRemainingTime);
        }
      }, 1000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [remainingTime, startTime]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              講義音声から教材自動生成
            </h1>
            <p className="text-xl text-gray-600">
              MP3音声ファイルから、講義録や教材を自動で生成しましょう
            </p>
          <div className="mt-6">
            <button
              onClick={() => setShowRecords(!showRecords)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
            >
              {showRecords ? "新規作成に戻る" : "講義録一覧を見る"}
            </button>
          </div>
        </div>

        {/* プロセスステップ表示 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">講義録生成プロセス</h2>
          <div className="space-y-4">
            {processSteps.map((step) => (
              <div key={step.id} className="flex items-center space-x-4">
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step.status === "completed" 
                    ? "bg-green-100 text-green-800" 
                    : step.status === "in_progress"
                    ? "bg-blue-100 text-blue-800"
                    : "bg-gray-100 text-gray-600"
                }`}>
                  {step.status === "completed" ? "✓" : step.id}
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${
                    step.status === "completed" 
                      ? "text-green-800" 
                      : step.status === "in_progress"
                      ? "text-blue-800"
                      : "text-gray-600"
                  }`}>
                    {step.title}
                  </p>
                  {step.result && step.status === "completed" && (
                    <div className="mt-2">
                      <button
                        onClick={() => {
                          const blob = new Blob([step.result || ""], { type: "text/plain" });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement("a");
                          a.href = url;
                          a.download = `step-${step.id}-${step.title.split(' ')[0]}.txt`;
                          a.click();
                          URL.revokeObjectURL(url);
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        ダウンロード
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 講義録一覧表示 */}
        {showRecords && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">講義録一覧</h2>
            {lectureRecords.length === 0 ? (
              <p className="text-gray-500 text-center py-8">まだ講義録がありません</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        講義名
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        講義録
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        音声時間
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        作成日時
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {lectureRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {record.title}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.finalTranscript ? (
                            <button
                              onClick={() => {
                                const blob = new Blob([record.finalTranscript], { type: "text/plain" });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement("a");
                                a.href = url;
                                a.download = `${record.title}-transcript.txt`;
                                a.click();
                                URL.revokeObjectURL(url);
                              }}
                              className="text-blue-600 hover:text-blue-800 underline"
                            >
                              ダウンロード
                            </button>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {Math.floor(record.audioDuration / 60)}分{record.audioDuration % 60}秒
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.createdAt}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <button
                            onClick={() => deleteLectureRecord(record.id)}
                            className="text-red-600 hover:text-red-800 underline"
                          >
                            削除
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {!showRecords && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* 音声ファイルアップロードエリア */}
          <div className="space-y-6">
            <div>
              <label htmlFor="audioFile" className="block text-sm font-medium text-gray-700 mb-2">
                MP3音声ファイル
              </label>
              <input
                type="file"
                id="audioFile"
                accept=".mp3,audio/mpeg"
                onChange={handleFileChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 ${
                  videoFile && !isValidAudioFile(videoFile) 
                    ? "border-red-300 bg-red-50" 
                    : "border-gray-300 bg-white"
                }`}
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

            <div>
              <label htmlFor="videoTitle" className="block text-sm font-medium text-gray-700 mb-2">
                講義タイトル（任意）
              </label>
              <input
                type="text"
                id="videoTitle"
                value={videoTitle}
                onChange={handleTitleChange}
                placeholder="例: 2024年度新入社員研修 - 第1回"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500 bg-white"
                disabled={isProcessing}
              />
            </div>

            {/* 処理ボタン */}
            <div className="text-center">
              <button
                onClick={handleProcess}
                disabled={!videoFile || !isValidAudioFile(videoFile) || isProcessing}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-8 rounded-lg transition-colors"
              >
                {isProcessing ? "処理中..." : "講義録を生成"}
              </button>
            </div>
          </div>

          {/* 進捗表示 */}
          {isProcessing && (
            <div className="mt-8">
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 mb-4">
                  {currentStep}
                </p>
                
                {/* カウントダウンタイマー */}
                {remainingTime !== null && (
                  <div className="mb-6">
                    <div className="text-4xl font-bold text-blue-600 mb-2">
                      {formatTime(remainingTime)}
                    </div>
                    <p className="text-sm text-gray-600">
                      残り時間
                    </p>
                  </div>
                )}
                
                {/* 推定時間と音声情報 */}
                {estimatedTime && (
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>推定処理時間: 約{estimatedTime}分</p>
                    {videoInfo && (
                      <>
                        <p>音声の長さ: {Math.floor(videoInfo.duration / 60)}分{videoInfo.duration % 60}秒</p>
                        <p>セグメント数: {videoInfo.segmentCount}個</p>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 結果表示 */}
          {result && (
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">最終結果</h3>
                {videoInfo && (
                  <div className="text-sm text-gray-500">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {Math.floor(videoInfo.duration / 60)}分{videoInfo.duration % 60}秒
                    </span>
                    <span className="ml-2 bg-green-100 text-green-800 px-2 py-1 rounded">
                      {videoInfo.segmentCount}セグメント
                    </span>
                  </div>
                )}
              </div>
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">{result}</pre>
              </div>
              <div className="mt-4 flex gap-4">
                <button
                  onClick={() => {
                    const blob = new Blob([result], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "final-lecture-transcript.txt";
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  最終版をダウンロード
                </button>
                <button
                  onClick={() => {
                    setResult(null);
                    resetProcessSteps();
                    stopCountdown();
                  }}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  新しい音声を処理
                </button>
              </div>
            </div>
          )}
          </div>
        )}

        {/* 機能説明 */}
        {!showRecords && (
          <div className="mt-12 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">音声ファイルアップロード</h3>
            <p className="text-gray-600">MP3音声ファイルを簡単にアップロード</p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI文字起こし</h3>
            <p className="text-gray-600">Whisper AIによる高精度な日本語文字起こし</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">教材生成</h3>
            <p className="text-gray-600">講義録、サマリー、テキストブックを自動生成</p>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
