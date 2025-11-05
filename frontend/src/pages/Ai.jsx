// src/pages/Ai.jsx

import React, { useState, useRef, useEffect, useMemo } from "react";
import Sidebar from "../components/Sidebar";
import LoadingScreen from "../components/LoadingScreen";
import { useAuth } from "../context/AuthContext";
import ApiKeyWarning from "../components/ApiKeyWarning";
import RepoPanel from "../components/RepoPanel";
import ChatPanel from "../components/ChatPanel";
import { Github, AlertTriangle } from "lucide-react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";
const loadingMessages = {
  ingest: [
    "Sneaking into your repo… hope there are no bugs!",
    "Waking up the code monkeys…",
    "Polishing your commits…",
    "Dusting off those README files…",
    "Counting stars on your repo…",
    "Petting the code cats…",
    "Untangling spaghetti code…",
    "Hunting for Easter eggs in your repo…",
    "Convincing GitHub to share secrets…",
    "Packing your code snacks…"
  ],
  chatHistory: [
    "Digging up your previous wisdom…",
    "Scrolling through your genius…",
    "Reading your chat like a detective…",
    "Warming up the old conversations…",
    "Sweeping digital footprints…"
  ],
  switchRepo: [
    "Packing up your stuff…",
    "Moving to a new repo neighborhood…",
    "Changing addresses in code city…",
    "Waving goodbye to your old repo…",
    "Dusting off for a fresh start…"
  ],
  deleteMessage: [
    "Shredding your message into digital confetti…",
    "Feeding your message to the recycle bin monster…",
    "Disappearing your message like a magician…",
    "Pretending your message never existed…",
    "Launching your message into the void…"
  ],
  restore: [
    "Resurrecting your last chat…",
    "Summoning your old AI conversations…",
    "Rewinding the code memories…",
    "Teleporting to your last session…"
  ]
};

/** Inline progress UI with checkpoints */
function IngestProgress({ visible, progress, checkpoints, onCancel }) {
  if (!visible) return null;
  const pct = Math.max(0, Math.min(100, progress));
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-[min(680px,90vw)] bg-[#0d1117] border border-[#21262d] rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white">Indexing your repo</h3>
          <button
            className="text-gray-400 hover:text-gray-200 text-sm px-2 py-1 rounded-md border border-transparent hover:border-[#30363d]"
            onClick={onCancel}
          >
            Cancel
          </button>
        </div>
        <div className="w-full h-3 rounded-full bg-[#161b22] border border-[#30363d] overflow-hidden">
          <div
            className="h-full bg-[#2ea043] transition-all duration-300"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="mt-2 text-xs text-gray-400">{pct}% complete</div>

        <ul className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-2">
          {checkpoints.map((cp, idx) => (
            <li
              key={idx}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                cp.done
                  ? "border-[#2ea043]/30 bg-[#1a2125]"
                  : "border-[#2e3440]/40 bg-transparent"
              }`}
            >
              <span className={`inline-flex h-2.5 w-2.5 rounded-full ${cp.done ? "bg-[#2ea043]" : "bg-[#6e7681]"}`} />
              <span className={`text-sm ${cp.done ? "text-gray-100" : "text-gray-400"}`}>{cp.label}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[13px] text-gray-400">
          Chat will be available once your entire repository has been indexed and analyzed. Please wait until the process is fully complete.
        </p>
      </div>
    </div>
  );
}

export default function Ai() {
  const { user, logout, provider } = useAuth();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");
  const [apiKeyExists, setApiKeyExists] = useState(undefined);
  const [repoData, setRepoData] = useState(null);
  const [chat, setChat] = useState([
    { sender: "ai", text: "Paste your GitHub repo URL to start chatting about your code.", avatar: "/logo.png" }
  ]);
  const [msg, setMsg] = useState("");
  const [loadingRepo, setLoadingRepo] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);
  const [globalLoading, setGlobalLoading] = useState({ show: false, messages: ["Loading..."], subtext: "" });
  const [submitted, setSubmitted] = useState(false);

  const chatRef = useRef();

  // New: ingest progress UI state
  const initialCheckpoints = useMemo(
    () => ([
      { key: "kickoff",    label: "Starting ingestion", done: false },
      { key: "streaming",  label: "Streaming repo files", done: false },
      { key: "chunking",   label: "Chunking content", done: false },
      { key: "upserting",  label: "Upserting vectors", done: false },
      { key: "analytics",  label: "Building repo analytics", done: false },
      { key: "ready",      label: "Ready to chat", done: false },
    ]),
    []
  );
  const [ingestProgress, setIngestProgress] = useState(0);
  const [checkpoints, setCheckpoints] = useState(initialCheckpoints);
  const [showIngestOverlay, setShowIngestOverlay] = useState(false);
  const progressTimerRef = useRef(null);
  const pollTimerRef = useRef(null);

  useEffect(() => {
    async function checkActiveRepo() {
      if (!user?.id) {
        setSubmitted(false);
        setRepoUrl("");
        setRepoData(null);
        setChat([
          { sender: "ai", text: "Paste your GitHub repo URL to start chatting about your code.", avatar: "/logo.png" }
        ]);
        return;
      }
      setGlobalLoading({ show: true, messages: loadingMessages.restore, subtext: "" });
      try {
        const res = await fetch(`${BACKEND_URL}/api/repo/get_active_repo`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id }),
        });
        const data = await res.json();
        if (data?.repo_url) {
          setRepoUrl(data.repo_url);
          setSubmitted(true);
          fetchRepoMeta(data.repo_url);
          await fetchUserChatHistory(user.id);
        } else {
          setRepoUrl("");
          setRepoData(null);
          setSubmitted(false);
          setChat([
            { sender: "ai", text: "Paste your GitHub repo URL to start chatting about your code.", avatar: "/logo.png" }
          ]);
        }
      } catch {
        setRepoUrl("");
        setRepoData(null);
        setSubmitted(false);
        setChat([
          { sender: "ai", text: "Paste your GitHub repo URL to start chatting about your code.", avatar: "/logo.png" }
        ]);
      }
      setGlobalLoading({ show: false, messages: [], subtext: "" });
    }
    checkActiveRepo();
  }, [user?.id]);

  async function fetchUserChatHistory(userId) {
    setGlobalLoading({ show: true, messages: loadingMessages.chatHistory, subtext: "" });
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai/get_chat_history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      if (res.ok && Array.isArray(data.messages) && data.messages.length > 0) {
        const formatted = data.messages.map((msg) => ({
          sender: msg.role === "assistant" ? "ai" : "user",
          text: msg.content,
          id: msg.id,
          avatar: msg.role === "assistant"
            ? "/logo.png"
            : (user?.avatar_url || user?.picture || "/logo.png"),
        }));
        setChat(formatted);
      } else {
        setChat([
          { sender: "ai", text: "Repo loaded! Now ask me anything about your codebase.", avatar: "/logo.png" }
        ]);
      }
    } catch {
      setChat([
        { sender: "ai", text: "Repo loaded! Now ask me anything about your codebase.", avatar: "/logo.png" }
      ]);
    }
    setGlobalLoading({ show: false, messages: [], subtext: "" });
  }

  async function handleDeleteMessage(msgId) {
    setGlobalLoading({ show: true, messages: loadingMessages.deleteMessage, subtext: "" });
    try {
      await fetch(`${BACKEND_URL}/api/ai/delete_message?msg_id=${msgId}&user_id=${user.id}`, {
        method: "DELETE",
      });
      await fetchUserChatHistory(user.id);
    } catch {}
    setGlobalLoading({ show: false, messages: [], subtext: "" });
  }

  useEffect(() => {
    const fetchAnyKey = async () => {
      if (!user?.id) {
        setApiKeyExists(false);
        return;
      }
      try {
        const [openaiRes, geminiRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/ai/get_api_key`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user.id, provider: "openai" }),
          }),
          fetch(`${BACKEND_URL}/api/ai/get_api_key`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user.id, provider: "gemini" }),
          }),
        ]);
        const [openaiData, geminiData] = await Promise.all([openaiRes.json(), geminiRes.json()]);
        const exists = (openaiRes.ok && openaiData?.exists) || (geminiRes.ok && geminiData?.exists);
        setApiKeyExists(Boolean(exists));
      } catch {
        setApiKeyExists(false);
      }
    };
    fetchAnyKey();
  }, [user?.id, globalLoading]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chat, loadingChat]);

  async function fetchRepoMeta(repo_url) {
    try {
      const res = await fetch(`${BACKEND_URL}/api/repo/metadata`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id }),
      });

      if (!res.ok) {
        setRepoData(null);
        return;
      }

      const data = await res.json();
      const analytics = data.analytics;

      setRepoData({
        name: analytics.repo_name,
        owner: analytics.owner,
        avatar_url: analytics.contributors[0]?.avatar_url || "/logo.png",
        stars: analytics.stars,
        forks: analytics.forks,
        description: analytics.description,
        html_url: `https://github.com/${analytics.owner}/${analytics.repo_name}`,
        homepage: analytics.homepage,
        main_language: analytics.language,
        license: analytics.license,
        topics: analytics.topics,
        profile: {
          name: analytics.owner,
          avatar_url: analytics.contributors[0]?.avatar_url || "/logo.png",
          github: `https://github.com/${analytics.owner}`,
        },
      });
    } catch {
      setRepoData(null);
    }
  }

  function startProgressUI() {
    setShowIngestOverlay(true);
    setIngestProgress(5);
    setCheckpoints((prev) => prev.map(c => c.key === "kickoff" ? { ...c, done: true } : c));
    if (progressTimerRef.current) clearInterval(progressTimerRef.current);
    progressTimerRef.current = setInterval(() => {
      setIngestProgress((p) => (p < 90 ? p + 1 : p));
    }, 400);
    // staged checkpoints to give user visible milestones
    setTimeout(() => setCheckpoints((prev) => prev.map(c => c.key === "streaming" ? { ...c, done: true } : c)), 1200);
    setTimeout(() => setCheckpoints((prev) => prev.map(c => c.key === "chunking" ? { ...c, done: true } : c)), 3200);
    setTimeout(() => setCheckpoints((prev) => prev.map(c => c.key === "upserting" ? { ...c, done: true } : c)), 5200);
  }

  function stopProgressUI(finalizeReady = false) {
    if (progressTimerRef.current) clearInterval(progressTimerRef.current);
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    if (finalizeReady) {
      setIngestProgress(100);
      setCheckpoints((prev) =>
        prev.map((c) =>
          c.key === "analytics" || c.key === "ready" ? { ...c, done: true } : c
        )
      );
      setTimeout(() => setShowIngestOverlay(false), 600);
    } else {
      setShowIngestOverlay(false);
    }
  }

  async function handleRepoSubmit(e) {
    e.preventDefault();
    if (!repoUrl.trim()) {
      alert("Please enter a repo URL.");
      return;
    }
    if (!apiKeyExists) {
      alert("Please add your OpenAI or Gemini API key from the sidebar first.");
      return;
    }
    setLoadingRepo(true);
    setGlobalLoading({ show: true, messages: loadingMessages.ingest, subtext: "Please do not close your browser. It's magic time." });

    // reset progress UI
    setCheckpoints(initialCheckpoints);
    startProgressUI();

    try {
      const res = await fetch(`${BACKEND_URL}/api/repo/ingest_repo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          repo_url: repoUrl,
          provider: provider,
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Ingestion failed.");
      }

      // Begin polling for metadata readiness (built async on server)
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      pollTimerRef.current = setInterval(async () => {
        try {
          const r = await fetch(`${BACKEND_URL}/api/repo/metadata`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user.id }),
          });
          if (r.ok) {
            const meta = await r.json();
            if (meta?.analytics?.repo_name) {
              setCheckpoints((prev) => prev.map(c => c.key === "analytics" ? { ...c, done: true } : c));
              await fetchRepoMeta(repoUrl);
              await fetchUserChatHistory(user.id);
              setSubmitted(true);
              setCheckpoints((prev) => prev.map(c => c.key === "ready" ? { ...c, done: true } : c));
              stopProgressUI(true);
              setGlobalLoading({ show: false, messages: [], subtext: "" });
            }
          }
        } catch {}
      }, 1500);
    } catch (err) {
      alert("Error loading repo: " + err.message);
      setSubmitted(false);
      stopProgressUI(false);
    } finally {
      setLoadingRepo(false);
      setGlobalLoading({ show: false, messages: [], subtext: "" });
    }
  }

  async function handleSend(e) {
    e.preventDefault();
    if (!msg.trim() || !user || !repoData || !apiKeyExists) {
      alert("Please enter a message and ensure your OpenAI or Gemini API key is set in the sidebar.");
      return;
    }
    const newChat = [
      ...chat,
      {
        sender: "user",
        text: msg,
        avatar: user?.avatar_url || user?.picture || "/logo.png",
      },
    ];
    setChat(newChat);
    setMsg("");
    setLoadingChat(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          message: msg,
          provider: provider,
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Chat request failed.");
      }
      const data = await res.json();
      const updatedChat = [
        ...newChat,
        {
          sender: "ai",
          text: data.result || "(No answer)",
          avatar: "/logo.png",
        },
      ];
      setChat(updatedChat);
    } catch (err) {
      setChat((c) => [
        ...c,
        {
          sender: "ai",
          text: "Error: " + err.message,
          avatar: "/logo.png",
        },
      ]);
    } finally {
      setLoadingChat(false);
    }
  }

  async function handleNewRepo() {
    if (window.confirm("Switching repo will clear the current chat and context. Continue?")) {
      setGlobalLoading({ show: true, messages: loadingMessages.switchRepo, subtext: "" });
      try {
        await fetch(`${BACKEND_URL}/api/repo/switch_repo`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id }),
        });
      } catch {}
      setRepoUrl("");
      setRepoData(null);
      setSubmitted(false);
      setChat([
        { sender: "ai", text: "Paste your GitHub repo URL to start chatting about your code.", avatar: "/logo.png" }
      ]);
      setGlobalLoading({ show: false, messages: [], subtext: "" });
    }
  }

  useEffect(() => {
    return () => {
      if (progressTimerRef.current) clearInterval(progressTimerRef.current);
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  const logoutWithClear = async () => logout();
  const showApiKeyBlur = apiKeyExists === false;

  return (
    <div className="flex min-h-screen bg-[#161b22] flex-col relative overflow-hidden">
      {globalLoading.show && (
        <LoadingScreen
          messages={globalLoading.messages}
          subtext={globalLoading.subtext}
        />
      )}

      {/* Ingest progress overlay with checkpoints */}
      <IngestProgress
        visible={showIngestOverlay}
        progress={ingestProgress}
        checkpoints={checkpoints}
        onCancel={() => {
          stopProgressUI(false);
        }}
      />

      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} onLogout={logoutWithClear} />
      <div className="flex items-center justify-between px-6 py-4 bg-[#161b22] border-b border-[#21262d] w-full z-20 h-16">
        <div className="flex items-center gap-2">
          <img src="/logo.png" className="h-8 w-8 rounded-full" alt="gitRAG" />
          <span className="font-bold text-[#2ea043] ml-1 text-xl">AI Chat</span>
        </div>
        {!sidebarOpen && (
          <button
            className="z-50 p-0 outline-none border-none bg-transparent"
            style={{ boxShadow: "none" }}
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            <img
              src={user?.avatar_url || user?.picture || "/logo.png"}
              className="h-10 w-10 rounded-full border border-[#2ea043] bg-[#161b22]"
              alt="Profile"
            />
          </button>
        )}
      </div>
      <div className="relative flex-1 flex flex-col w-full min-h-0">
        {showApiKeyBlur && (
          <div className="absolute inset-0 z-40 flex items-center justify-center pointer-events-none">
            <div className="absolute inset-0 bg-[#0d1117]/70 backdrop-blur-[6px] transition-all duration-200" />
            <div className="relative z-50 pointer-events-auto">
              <ApiKeyWarning />
            </div>
          </div>
        )}
        <main className={`flex flex-col flex-1 w-full overflow-hidden transition-all duration-300 ${showApiKeyBlur ? "pointer-events-none select-none" : ""}`}>
          {!submitted && (
            <div className="flex flex-col items-center justify-center flex-1 px-4">
              <form
                className="w-full max-w-2xl mx-auto flex flex-col gap-4 bg-[#20252b] border border-[#232b36] rounded-lg px-4 py-6 shadow-sm"
                onSubmit={handleRepoSubmit}
                autoComplete="off"
              >
                <label className="flex flex-col gap-1">
                  <span className="text-sm text-gray-300 font-semibold">GitHub Repo URL</span>
                  <div className="flex gap-2">
                    <input
                      className="flex-1 bg-transparent border border-[#232b36] rounded-lg px-4 py-2 text-base text-gray-200 placeholder-gray-500 outline-none focus:border-[#2ea043] focus:ring-1 focus:ring-[#2ea043] transition"
                      placeholder="https://github.com/owner/repo"
                      value={repoUrl}
                      onChange={e => setRepoUrl(e.target.value)}
                      spellCheck={false}
                      required
                      disabled={loadingRepo || !apiKeyExists}
                    />
                    <button
                      type="submit"
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#2ea043] hover:bg-[#238636] text-white font-semibold text-base shadow transition"
                      disabled={loadingRepo || !apiKeyExists}
                    >
                      {loadingRepo ? (
                        <span className="animate-spin mr-1">⏳</span>
                      ) : (
                        <Github className="w-5 h-5" />
                      )}
                      {loadingRepo ? "Loading..." : "Submit"}
                    </button>
                  </div>
                </label>
                <div className="text-xs text-gray-400 mt-2 italic">
                  <b>Your OpenAI or Gemini API key is stored securely and can be removed completely from our system whenever you want using the sidebar. It is only accessible to you.</b>
                </div>
              </form>
              {apiKeyExists === false && !sidebarOpen && <ApiKeyWarning />}
              <div className="w-full max-w-2xl mx-auto mt-8 bg-[#21262d] border border-[#2ea043]/20 rounded-lg p-5 shadow-sm">
                <h2 className="text-lg font-bold text-[#2ea043] mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-[#fbbf24]" />
                  Setup Guide: Using Your Own API Key
                </h2>
                <ol className="text-sm text-gray-200 space-y-2 list-decimal list-inside pl-2 mb-3">
                  <li>
                    For <b>OpenAI</b>, create a key at{" "}
                    <a
                      href="https://platform.openai.com/api-keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#2ea043] underline"
                    >
                      platform.openai.com/api-keys
                    </a>
                    .
                  </li>
                  <li>
                    For <b>Gemini</b>, create a key at{" "}
                    <a
                      href="https://aistudio.google.com/app/apikey"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#2ea043] underline"
                    >
                      aistudio.google.com/app/apikey
                    </a>
                    .
                  </li>
                  <li>Paste either key in the sidebar. Having any one of them is enough to proceed.</li>
                  <li>Use only your personal key; you can remove it anytime from the sidebar.</li>
                </ol>
              </div>
            </div>
          )}
          {submitted && repoData && (
            <div className="w-full max-w-[99vw] mx-auto flex flex-1 min-h-0 flex-col md:flex-row gap-4 p-4">
              <RepoPanel repoData={repoData} handleNewRepo={handleNewRepo} />
              <ChatPanel
                chat={chat}
                msg={msg}
                setMsg={setMsg}
                loadingChat={loadingChat}
                onSend={handleSend}
                canChat={apiKeyExists}
                chatRef={chatRef}
                onDeleteMessage={handleDeleteMessage}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
