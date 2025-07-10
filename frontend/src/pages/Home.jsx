import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { Search, GitBranch, BarChart2, KeyRound, MessageSquare, Star } from "lucide-react";
import PointCloudSphere from "../components/PointCloudSphere";

// Typing animation for logo
function TypingGitRAG() {
  const text = "gitRAG";
  const [display, setDisplay] = useState("");
  const [i, setI] = useState(0);
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDisplay(text.slice(0, i + 1));
      setI(i === text.length ? 0 : i + 1);
    }, i === text.length ? 900 : 120);
    return () => clearTimeout(timeout);
  }, [i]);
  return <span className="font-bold text-[#2ea043] ml-1">{display}</span>;
}

// --- Feature list (aligned with your actual features) ---
const features = [
  {
    icon: MessageSquare,
    title: "AI Code Chat",
    description: "Chat with an AI assistant to understand code, get summaries, and answer codebase questions."
  },
  {
    icon: GitBranch,
    title: "Hierarchical File View",
    description: "Explore your repo’s complete file structure with direct file content preview and metadata."
  },
  {
    icon: BarChart2,
    title: "Repo Analytics",
    description: "Get instant repo analytics—languages, stats, dependency graph, and contributors at a glance."
  },
  {
    icon: Search,
    title: "Semantic Code Search",
    description: "Find files or functions using semantic search powered by embeddings—not just keywords."
  },
  {
    icon: KeyRound,
    title: "Secure API Key Management",
    description: "Your OpenAI API key is encrypted per-user, can be changed or removed at any time from the sidebar."
  },
  {
    icon: Star,
    title: "One-Click Setup",
    description: "Log in, paste a GitHub repo URL, and start chatting—no config or local setup needed."
  }
];

// --- Footer ---
function Footer({ user }) {
  return (
    <footer className="w-full bg-[#161b22] border-t border-[#232b36] py-8 mt-16">
      <div className="max-w-4xl mx-auto flex flex-col items-center gap-3">
        <div className="flex items-center gap-3 mb-1">
          <img
            src="/logo.png"
            className="h-10 w-10 rounded-full border border-[#2ea043] shadow"
            alt="gitRAG"
          />
          <span className="text-gray-400 text-lg font-bold tracking-wide">gitRAG</span>
        </div>
        <span className="text-gray-400 text-xs mb-1">
          &copy; {new Date().getFullYear()} gitRAG. All rights reserved.
        </span>
        {user && (
          <span className="flex items-center gap-2 text-xs text-gray-500">
            <img
              src={user.avatar_url || user.picture || "/logo.png"}
              className="h-7 w-7 rounded-full border border-[#2ea043]"
              alt="Profile"
            />
            {user.name || user.login || user.email}
          </span>
        )}
      </div>
    </footer>
  );
}

export default function Home() {
  const { user } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-[#161b22] flex-col relative">
      {/* --- NAVBAR --- */}
      <div className="flex items-center justify-between px-6 py-4 bg-[#161b22] border-b border-[#21262d] w-full">
        <div className="flex items-center gap-2">
          <img src="/logo.png" className="h-8 w-8 rounded-full" alt="gitRAG" />
          <TypingGitRAG />
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
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />

      {/* --- HERO Section --- */}
      <main className="flex flex-col flex-1 items-center justify-center bg-[#161b22] text-gray-200 p-4 sm:p-8 w-full">
        <div
          className="w-full max-w-8xl relative z-10 rounded-2xl overflow-hidden mt-8 mb-20"
          style={{
            backgroundImage: "url('/background.gif')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            minHeight: "500px"
          }}
        >
          {/* Overlay */}
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm pointer-events-none"></div>
          {/* Flex row for hero */}
          <div className="relative flex flex-col md:flex-row items-center justify-center w-full h-full p-8 z-10">
            {/* Left */}
            <div className="flex-1 min-w-[270px] md:min-w-[360px] max-w-lg flex flex-col items-start text-left z-10">
              <h1 className="text-4xl md:text-5xl font-extrabold mb-6 text-[#2ea043] leading-tight drop-shadow-lg">
                Analyse Any GitHub Repo with <span className="text-[#2ea043]">AI</span>
              </h1>
              <p className="text-lg text-gray-100 mb-6 drop-shadow-md max-w-sm">
                <span className="font-medium">
                  Paste a GitHub repo URL, add your OpenAI key, and start chatting with your codebase using advanced RAG AI.
                </span>
              </p>
              <div className="flex flex-row gap-4 w-full">
                <a
                  href="/ai"
                  className="bg-[#2ea043] hover:bg-[#268839] px-8 py-4 rounded-lg font-semibold text-lg text-white transition-all duration-300 transform hover:scale-105 flex items-center gap-3 shadow-lg shadow-[#2ea043]/30"
                >
                  <MessageSquare size={20} /> AI Chat
                </a>
                <a
                  href="/repo"
                  className="bg-[#232b36] hover:bg-[#20252b] border border-[#2ea043] px-8 py-4 rounded-lg font-semibold text-lg text-[#2ea043] transition-all duration-300 transform hover:scale-105 flex items-center gap-3 shadow"
                >
                  <GitBranch size={20} /> Explore Repo
                </a>
              </div>
            </div>
            {/* Divider */}
            <div className="hidden md:flex h-[70%] w-[2px] bg-white opacity-80 mx-10 my-12 rounded-full" />
            {/* Right: 3D Point Cloud Sphere */}
            <div className="flex-1 flex items-center justify-center min-w-[320px] h-[370px] z-10">
              <PointCloudSphere />
            </div>
          </div>
        </div>

        {/* --- Features Section --- */}
        <div className="max-w-6xl w-full mt-8 pb-8">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-4 text-white">Why Use gitRAG?</h2>
            <p className="text-lg text-gray-400">
              Features designed to help you{" "}
              <span className="text-[#2ea043]">
                chat, analyze, and explore
              </span>{" "}
              codebases faster and smarter.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f, i) => (
              <div
                key={i}
                className="bg-[#21262d] border border-[#2ea04322] rounded-2xl p-6 flex flex-col gap-4 shadow-md hover:shadow-[#2ea04333] transition-transform duration-300 hover:scale-105 group"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-[#2ea043]/10 p-3 rounded-xl">
                    <f.icon size={26} className="text-[#2ea043]" />
                  </div>
                  <span className="font-bold text-lg text-gray-200">
                    {f.title}
                  </span>
                </div>
                <div className="text-gray-400 group-hover:text-gray-200 transition">
                  {f.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
      {/* --- Footer --- */}
      <Footer user={user} />
    </div>
  );
}
