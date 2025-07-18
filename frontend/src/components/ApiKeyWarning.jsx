import React from "react";
import { AlertTriangle } from "lucide-react";

export default function ApiKeyWarning() {
  return (
    <div className="flex flex-col items-start gap-2 text-yellow-400 text-base bg-yellow-900/30 rounded-lg p-3 mb-6 max-w-md shadow">
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-5 h-5" />
        <span className="font-semibold">OpenAI API Key Missing</span>
      </div>
      <p>You have not added your OpenAI API key.</p>
      <p>Please add your key from the sidebar before accessing GitHub repo chat or analysis features.</p>
      <p className="text-white">And refresh the page once you have added your OpenAI API key.</p>
    </div>
  );
}
