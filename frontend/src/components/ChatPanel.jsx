import React, { useRef, useEffect } from "react";
import { Send } from "lucide-react";
import ChatBubble from "./ChatBubble";

export default function ChatPanel({
  chat,
  msg,
  setMsg,
  loadingChat,
  onSend,
  canChat,
  chatRef,
  onDeleteMessage
}) {
  return (
    <div className="md:w-[75%] w-full flex flex-col bg-[#20252b] border border-[#232b36] rounded shadow-md relative overflow-hidden">
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto p-4 pb-2"
        style={{
          height: 'calc(100vh - 200px)',
          maxHeight: 'calc(100vh - 200px)',
          scrollBehavior: 'smooth'
        }}
      >
        {chat.map((c, i) => (
          <ChatBubble
            key={c.id ?? i}
            sender={c.sender}
            text={c.text}
            avatar={c.avatar}
            id={c.id}
            onDelete={onDeleteMessage}
            canDelete={typeof c.id === "number"}
          />
        ))}
        {loadingChat && (
          <div className="flex justify-start mb-4">
            <div className="px-4 py-3 rounded-lg max-w-[75%] shadow-sm bg-[#232b36] text-gray-400 border border-[#21262d]">
              <span className="animate-pulse">AI is typing…</span>
            </div>
          </div>
        )}
      </div>
      <div className="bg-[#181b20] border-t border-[#232b36] p-4 flex-shrink-0">
        <form
          onSubmit={onSend}
          className="flex items-center gap-2"
        >
          <input
            className="flex-1 bg-[#20252b] border border-[#232b36] rounded-lg px-4 py-3 text-base text-gray-200 placeholder-gray-500 outline-none focus:border-[#2ea043] focus:ring-1 focus:ring-[#2ea043] transition"
            placeholder={canChat ? "Ask anything about your repo…" : "Add your OpenAI API key from sidebar first..."}
            value={msg}
            onChange={e => setMsg(e.target.value)}
            spellCheck={false}
            autoFocus={canChat}
            onKeyDown={e => {
              if (e.key === "Enter" && !e.shiftKey && canChat) {
                e.preventDefault();
                onSend(e);
              }
            }}
            disabled={loadingChat || !canChat}
          />
          <button
            type="submit"
            className="flex items-center gap-1 px-4 py-3 rounded-lg bg-[#2ea043] hover:bg-[#238636] text-white font-semibold text-base shadow transition disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!msg.trim() || loadingChat || !canChat}
          >
            <Send className="w-4 h-4" />
            {loadingChat ? "Sending..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}