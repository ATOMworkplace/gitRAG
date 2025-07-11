// src/components/Sidebar.jsx
import React, { useRef, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  Brain,
  FolderGit2,
  Users,
  LogOut,
  KeyRound,
  XCircle,
  CheckCircle2,
  Home
} from "lucide-react";
import { useLocation, Link } from "react-router-dom";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

const NAV = [
  { label: "Home", href: "/home", icon: Home },
  { label: "AI", href: "/ai", icon: Brain },
  { label: "Repo", href: "/repo", icon: FolderGit2 },
  { label: "Feedback", href: "/feedback", icon: Users }
];

const Sidebar = ({ open, setOpen, onLogout }) => {
  const { user, logout } = useAuth();
  const avatar = user?.avatar_url || user?.picture || "/logo.png";
  const location = useLocation();
  const ref = useRef(null);

  // API Key state
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [storedApiKey, setStoredApiKey] = useState(""); // Masked key
  const [showInput, setShowInput] = useState(false);
  const [error, setError] = useState("");
  const [apiKeyValid, setApiKeyValid] = useState(false);
  const [validating, setValidating] = useState(false);

  // Load masked key from backend
  useEffect(() => {
    const fetchKey = async () => {
      if (!user?.id) {
        setStoredApiKey("");
        return;
      }
      try {
        const res = await fetch(`${BACKEND_URL}/ai/get_openai_key`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id })
        });
        const data = await res.json();
        if (res.ok && data.exists) {
          setStoredApiKey(data.masked_key);
        } else {
          setStoredApiKey("");
        }
      } catch (err) {
        setStoredApiKey("");
      }
    };
    fetchKey();
  }, [user?.id]);

  // Validate & add key via backend
  const handleValidateKey = async () => {
    const key = apiKeyInput.trim();
    if (!key) {
      setError("Please enter your OpenAI API key.");
      return;
    }
    if (!user?.id) {
      setError("User not found. Please log in again.");
      return;
    }
    setValidating(true);
    setError("");
    setApiKeyValid(false);
    try {
      const res = await fetch(`${BACKEND_URL}/ai/validate_openai_key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          openai_api_key: key,
          user_id: user.id
        })
      });
      const data = await res.json();
      if (res.ok && data.valid) {
        setApiKeyValid(true);
        setShowInput(false);
        setApiKeyInput("");
        setError("");
        // Refresh masked key from backend
        const keyRes = await fetch(`${BACKEND_URL}/ai/get_openai_key`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id })
        });
        const keyData = await keyRes.json();
        if (keyRes.ok && keyData.exists) setStoredApiKey(keyData.masked_key);
        else setStoredApiKey("");
      } else {
        setError(data.error || "Key validation failed.");
      }
    } catch (err) {
      setError("Network error. Could not validate key.");
    } finally {
      setValidating(false);
    }
  };

  // Remove key from backend
  const handleRemoveKey = async () => {
    if (!user?.id) {
      setError("User not found. Please log in again.");
      return;
    }
    setError("");
    setApiKeyValid(false);
    setApiKeyInput("");
    setShowInput(false);

    try {
      const res = await fetch(`${BACKEND_URL}/ai/delete_openai_key`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id })
      });
      const data = await res.json();
      if (res.ok && data.deleted) {
        setStoredApiKey("");
      } else {
        setError(data.detail || "Failed to delete API key from server.");
      }
    } catch (err) {
      setError("Network error. Could not remove key from server.");
    }
  };

  // Close sidebar on outside click
  useEffect(() => {
    if (!open) return;
    const handleClick = e => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open, setOpen]);

  return (
    <>
      <div
        ref={ref}
        className={`fixed top-0 right-0 h-full bg-gradient-to-br from-[#23272f] to-[#181b20] text-gray-100 shadow-xl transition-all duration-300 z-40 border-l border-gray-800 ${
          open ? "translate-x-0" : "translate-x-80"
        } rounded-l-3xl`}
        style={{ minWidth: "16rem" }}
      >
        {/* User Info */}
        <div className="flex flex-col items-center mt-10 mb-8">
          <img src={avatar} className="h-16 w-16 rounded-full border-4 border-[#238636] shadow-lg" alt="User" />
          <span className="mt-3 text-lg font-semibold text-gray-200 break-all text-center">
            {user?.name || user?.login || user?.email}
          </span>
          <span className="text-xs text-gray-400 mb-2">{user?.email || ""}</span>
          <button
            onClick={onLogout || logout}
            className="flex items-center gap-2 px-4 py-1.5 rounded-xl bg-[#238636] hover:bg-[#2ea043] text-white font-bold transition-all shadow mt-2"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-col gap-2 px-3">
          {NAV.map(item => {
            const isActive = location.pathname === item.href || (item.href !== "/" && location.pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-2 rounded-2xl text-base font-medium transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-[#21262d] text-[#238636] shadow border border-[#238636] font-bold"
                    : "hover:bg-[#232b36] hover:text-[#238636] text-gray-300"
                }`}
              >
                <Icon className="w-5 h-5" /> {item.label}
              </Link>
            );
          })}
        </nav>

        {/* API Key Management */}
        <div className="px-4 py-3 border-t border-gray-700 mt-6">
          <span className="text-sm text-gray-400">OpenAI API Key</span>

          {storedApiKey ? (
            <div className="flex items-center gap-2 mt-2">
              <span className="flex-1 bg-[#20252b] text-gray-200 px-3 py-2 rounded break-all">
                {storedApiKey}
              </span>
              <button
                onClick={handleRemoveKey}
                className="flex items-center gap-1 px-3 py-2 bg-red-600 rounded-lg text-white text-sm hover:bg-red-500 transition"
              >
                <XCircle className="w-4 h-4" /> Remove
              </button>
            </div>
          ) : showInput ? (
            <label className="flex flex-col gap-1 mt-2">
              <span className="text-sm text-gray-300 flex items-center gap-2 font-semibold">
                <KeyRound className="inline w-5 h-5 text-[#2ea043]" />
                {validating ? "Validating key..." : apiKeyValid ? "Key valid!" : "Enter your OpenAI API key"}
                {apiKeyValid && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                {!apiKeyValid && apiKeyInput && !validating && <XCircle className="w-4 h-4 text-red-400" />}
              </span>
              <div className="flex gap-2">
                <input
                  type="password"
                  placeholder="sk-..."
                  value={apiKeyInput}
                  onChange={e => {
                    setApiKeyInput(e.target.value);
                    setApiKeyValid(false);
                    if (error) setError("");
                  }}
                  className="flex-1 bg-[#161b22] border border-[#232b36] rounded-lg px-3 py-2 text-gray-200 placeholder-gray-500 outline-none focus:border-[#2ea043] focus:ring-1 focus:ring-[#2ea043] transition"
                />
                <button
                  type="button"
                  onClick={handleValidateKey}
                  disabled={validating || apiKeyValid}
                  className={`px-4 py-2 rounded-lg font-semibold text-base shadow transition ${
                    validating || apiKeyValid
                      ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                      : "bg-green-500 text-white hover:bg-green-400"
                  }`}
                >
                  {validating ? "Validating..." : apiKeyValid ? "Valid!" : "Validate"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowInput(false);
                    setApiKeyInput("");
                    setError("");
                  }}
                  className="px-4 py-2 rounded-lg text-base font-semibold bg-gray-700 hover:bg-gray-600 text-gray-200 transition"
                >
                  Cancel
                </button>
              </div>
              {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
            </label>
          ) : (
            <button
              onClick={() => setShowInput(true)}
              className="flex items-center gap-1 px-3 py-2 bg-blue-600 rounded-lg text-white text-sm hover:bg-blue-500 transition mt-2"
            >
              <KeyRound className="w-4 h-4" /> Add Key
            </button>
          )}
        </div>
      </div>

      {/* Blurry Overlay */}
      {open && <div className="fixed inset-0 z-30 backdrop-blur-[2px] bg-black/30" onClick={() => setOpen(false)} />}
    </>
  );
};

export default Sidebar;
