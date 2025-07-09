import React, { useEffect, useState } from "react";

export default function LoadingScreen({ messages = ["Loading..."], subtext = "" }) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    if (!messages?.length) return;
    setIdx(0);
    const timer = setInterval(() => setIdx(i => (i + 1) % messages.length), 3000);
    return () => clearInterval(timer);
  }, [messages]);

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-70 flex flex-col items-center justify-center">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[#2ea043] mb-6" />
      <div className="text-xl font-bold text-white mb-2">{messages?.[idx] || "Loading..."}</div>
      {subtext && <div className="text-gray-300 text-sm">{subtext}</div>}
    </div>
  );
}
