import React, { useEffect, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { materialDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { motion, AnimatePresence } from "framer-motion";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

// SVG icon components (all small)
const FolderIcon = (props) => (
  <svg className={props.className} fill="none" stroke="currentColor" viewBox="0 0 24 24" width={16} height={16}><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"></path></svg>
);
const FileIcon = (props) => (
  <svg className={props.className} fill="none" stroke="currentColor" viewBox="0 0 24 24" width={16} height={16}><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
);
const ChevronRightIcon = (props) => (
  <svg className={props.className} fill="none" stroke="currentColor" viewBox="0 0 24 24" width={14} height={14}><path d="m9 18 6-6-6-6"></path></svg>
);
const LayoutDashboardIcon = (props) => (
  <svg className={props.className} fill="none" stroke="currentColor" viewBox="0 0 24 24" width={16} height={16}><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
);
const NetworkIcon = (props) => (
  <svg className={props.className} fill="none" stroke="currentColor" viewBox="0 0 24 24" width={16} height={16}><rect x="16" y="16" width="6" height="6" rx="1"></rect><rect x="2" y="16" width="6" height="6" rx="1"></rect><rect x="9" y="2" width="6" height="6" rx="1"></rect><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"></path><path d="M12 12V8"></path></svg>
);

// Collapsible card
function CollapsibleCard({ title, icon, children, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="bg-[#232b36] rounded border border-gray-700/60 mb-2 overflow-hidden text-xs">
      <button
        className="w-full flex items-center justify-between p-2 text-left font-semibold text-gray-200 hover:bg-gray-700/40 transition-colors text-xs"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <div className="flex items-center gap-1">
          {icon}
          <span>{title}</span>
        </div>
        <ChevronRightIcon className={`transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`} />
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-2 border-t border-gray-700/60">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// --- File Tree ---
function FileTree({ tree, onFileClick, selectedFile, path = "" }) {
  const [openDirs, setOpenDirs] = useState({});
  if (!tree) return null;
  const toggleDir = (dirPath) => setOpenDirs((prev) => ({ ...prev, [dirPath]: !prev[dirPath] }));
  return (
    <ul className="text-xs text-gray-300">
      {Object.entries(tree).map(([key, value]) => {
        const fullPath = path ? `${path}/${key}` : key;
        const isDirectory = typeof value === "object" && value !== null;
        if (isDirectory) {
          const isOpen = openDirs[fullPath];
          return (
            <li key={fullPath} className="my-0.5">
              <button onClick={() => toggleDir(fullPath)} className="w-full text-left flex items-center gap-1 py-0.5 px-1 rounded hover:bg-gray-700/50 transition-colors text-xs">
                <ChevronRightIcon className={`w-3 h-3 transition-transform duration-150 ${isOpen ? 'rotate-90' : ''}`} />
                <FolderIcon className="w-3 h-3 text-sky-400" />
                <span className="font-medium">{key}</span>
              </button>
              {isOpen && (
                <div className="ml-2 pl-1 border-l border-gray-700/50">
                  <FileTree tree={value} path={fullPath} onFileClick={onFileClick} selectedFile={selectedFile} />
                </div>
              )}
            </li>
          );
        } else {
          const isSelected = selectedFile === fullPath;
          return (
            <li key={fullPath} className="my-0.5">
              <button
                className={`w-full text-left flex items-center gap-1 py-0.5 px-1 rounded transition-colors text-xs ${isSelected ? 'bg-[#2ea043]/20 text-[#2ea043]' : 'hover:bg-gray-700/50'}`}
                onClick={() => onFileClick(fullPath)}
              >
                <FileIcon className="w-3 h-3 ml-[14px] text-gray-400" />
                <span>{key}</span>
              </button>
            </li>
          );
        }
      })}
    </ul>
  );
}

// --- Language Distribution Visual ---
function LanguageBar({ languages }) {
  if (!languages) return null;
  const colors = [
    "#f7df1e", "#2965f1", "#e34c26", "#563d7c", "#b07219", "#3572A5", "#2ea043"
  ];
  const keys = Object.keys(languages);
  const total = Object.values(languages).reduce((a, b) => a + b, 0);
  let colorMap = {};
  keys.forEach((lang, i) => {
    colorMap[lang] = colors[i % colors.length];
  });

  return (
    <div>
      <div className="flex w-full h-2 rounded overflow-hidden border border-gray-700 mb-1">
        {keys.map((lang) => (
          <div
            key={lang}
            style={{
              width: `${((languages[lang] / total) * 100).toFixed(2)}%`,
              background: colorMap[lang],
            }}
            title={`${lang}: ${languages[lang]} lines`}
          ></div>
        ))}
      </div>
      <div className="flex flex-wrap gap-x-2 gap-y-0.5 text-[10px]">
        {keys.map((lang) => (
          <span key={lang} className="flex items-center gap-1">
            <span
              className="inline-block w-2 h-2 rounded"
              style={{ background: colorMap[lang] }}
            ></span>
            {lang} ({((languages[lang] / total) * 100).toFixed(1)}%)
          </span>
        ))}
      </div>
    </div>
  );
}

// --- Analytics Card ---
function RepoAnalytics({ analytics }) {
  if (!analytics || Object.keys(analytics).length === 0) return null;
  return (
    <CollapsibleCard title="Repo Analytics" icon={<LayoutDashboardIcon className="w-4 h-4 text-gray-400" />}>
      <div className="grid grid-cols-1 gap-y-1 text-xs">
        <div className="mb-1">
          <LanguageBar languages={analytics.languages} />
        </div>
        {Object.entries(analytics).map(([key, value]) => {
          if (key === "languages") return null;
          return (
            <div key={key} className="flex justify-between items-center">
              <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</span>
              <span className="text-gray-200 font-mono bg-gray-900/50 px-1 py-0.5 rounded">{String(value)}</span>
            </div>
          );
        })}
      </div>
    </CollapsibleCard>
  );
}

// --- Dependency Graph ---
function DependencyGraph({ graph }) {
  if (!graph || Object.keys(graph).length === 0) return null;
  return (
    <CollapsibleCard title="Dependency Graph" icon={<NetworkIcon className="w-4 h-4 text-gray-400" />}>
      <div className="overflow-x-auto text-[11px] text-gray-300 max-h-40 bg-gray-900/50 p-1 rounded">
        <pre className="whitespace-pre-wrap">{JSON.stringify(graph, null, 2)}</pre>
      </div>
    </CollapsibleCard>
  );
}

// --- Central File Viewer ---
function FileViewer({ filePath, fileContent, isLoading }) {
  if (!filePath) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 text-xs">
        <FileIcon className="w-10 h-10 mb-2" />
        <h3 className="text-lg font-semibold text-gray-400">Select a file</h3>
        <p>Choose a file from the explorer on the left to view its content.</p>
      </div>
    );
  }
  return (
    <div className="flex flex-col h-full text-xs">
      <div className="flex-shrink-0 p-2 border-b border-gray-700/60">
        <span className="font-mono text-[#2ea043]">{filePath}</span>
      </div>
      <div className="flex-grow bg-[#1c2128] rounded-b-lg overflow-auto p-2">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-gray-400 text-xs">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-200"></div>
            <span className="ml-2">Loading...</span>
          </div>
        ) : (
          <SyntaxHighlighter
            language={filePath.split('.').pop()}
            style={materialDark}
            wrapLongLines
            className="rounded"
            customStyle={{ background: "none", padding: 0, fontSize: 12 }}
          >
            {fileContent}
          </SyntaxHighlighter>
        )}
      </div>
    </div>
  );
}

// --- Main Page Component ---
export default function Repo() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [fileTree, setFileTree] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [dependencyGraph, setDependencyGraph] = useState(null);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [fileLoading, setFileLoading] = useState(false);

  // Fetch all repo data (real)
  useEffect(() => {
    async function fetchRepoMeta() {
      setLoading(true);
      setError("");
      setFileTree(null);
      setAnalytics(null);
      setDependencyGraph(null);
      setSelectedFile(null);
      setFileContent("");
      try {
        const res = await fetch(`${BACKEND_URL}/api/repo/metadata`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user?.id }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Failed to load repo metadata.");
        const data = await res.json();
        setFileTree(data.file_tree);
        setAnalytics(data.analytics);
        setDependencyGraph(data.dependency_graph);
      } catch (err) {
        setError(err.message || "Error loading repo.");
      }
      setLoading(false);
    }
    if (user?.id) fetchRepoMeta();
  }, [user?.id]);

  // File content fetch (real)
  const handleFileClick = async (filePath) => {
    setSelectedFile(filePath);
    setFileContent("");
    setFileLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/repo/get_file_content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user?.id, file_path: filePath }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Failed to load file content.");
      const data = await res.json();
      setFileContent(data.content);
    } catch (err) {
      setFileContent(`Error loading file: ${err.message}`);
    }
    setFileLoading(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#161b22] text-gray-300 font-sans text-xs">
      {/* Navbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-[#21262d] w-full text-xs">
        <div className="flex items-center gap-2">
          <img src="/logo.png" className="h-7 w-7 rounded-full" alt="gitRAG" />
          <span className="font-bold text-[#2ea043] ml-1 text-base">Repo Viewer</span>
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
              className="h-8 w-8 rounded-full border border-[#2ea043] bg-[#161b22]"
              alt="Profile"
            />
          </button>
        )}
      </div>
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} onLogout={logout} />

      {/* Main 3-column layout */}
      <div className="flex flex-grow overflow-hidden w-full">
        {/* Left: File Tree */}
        <aside className="w-1/4 lg:w-1/5 h-full bg-[#1c2128] border-r border-gray-700/60 p-1 flex flex-col min-h-0">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider p-1 mb-1">File Explorer</h2>
          <div className="flex-grow overflow-auto pr-1">
            {loading ? (
              <div className="p-1 text-gray-400 animate-pulse text-xs">Loading Tree...</div>
            ) : error ? (
              <div className="p-1 text-red-400 text-xs">{error}</div>
            ) : fileTree ? (
              <FileTree tree={fileTree} onFileClick={handleFileClick} selectedFile={selectedFile} />
            ) : (
              <div className="p-1 text-gray-500 text-xs">No repo loaded.</div>
            )}
          </div>
        </aside>
        {/* Center: File Viewer */}
        <main className="w-1/2 lg:w-3/5 h-full p-2 flex flex-col min-h-0">
          <div className="bg-[#232b36] rounded border border-gray-700/60 flex-1 min-h-0">
            <FileViewer filePath={selectedFile} fileContent={fileContent} isLoading={fileLoading} />
          </div>
        </main>
        {/* Right: Details */}
        <aside className="w-1/4 lg:w-1/5 h-full bg-[#1c2128] border-l border-gray-700/60 p-1 flex flex-col min-h-0">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider p-1 mb-1">Details</h2>
          <div className="flex flex-col gap-2 overflow-auto">
            {loading ? (
              <div className="p-1 text-gray-400 animate-pulse text-xs">Loading Details...</div>
            ) : (
              <>
                <RepoAnalytics analytics={analytics} />
                <DependencyGraph graph={dependencyGraph} />
              </>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
