import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { Bug, AlertTriangle, MessageSquare, Send, CheckCircle, Star } from "lucide-react";

// --- Typing Animation for gitRAG ---
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

// --- Feedback Categories ---
const feedbackCategories = [
  {
    icon: Bug,
    title: "Bug Report",
    description: "Report any bugs, errors, or unexpected behavior",
    color: "text-red-400",
    bgColor: "bg-red-400/10",
  },
  {
    icon: AlertTriangle,
    title: "Feature Request",
    description: "Suggest new features or improvements",
    color: "text-yellow-400",
    bgColor: "bg-yellow-400/10",
  },
  {
    icon: MessageSquare,
    title: "General Feedback",
    description: "Share your thoughts and suggestions",
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
  },
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

export default function Feedback() {
  const { user } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [formData, setFormData] = useState({
    category: "bug",
    title: "",
    description: "",
    steps: "",
    expectedBehavior: "",
    actualBehavior: "",
    browserInfo: "",
    additionalInfo: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Auto-fill browser and system info
  useEffect(() => {
    const browserInfo = `Browser: ${navigator.userAgent}\nScreen Resolution: ${screen.width}x${screen.height}\nTimezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}\nLanguage: ${navigator.language}`;
    setFormData(prev => ({ ...prev, browserInfo }));
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Prepare email data
      const emailData = {
        to: "charchitgithub@gmail.com",
        subject: `[gitRAG Feedback] ${formData.category.toUpperCase()}: ${formData.title}`,
        body: `
Feedback Category: ${formData.category.toUpperCase()}
Title: ${formData.title}
User: ${user?.name || user?.login || user?.email || "Anonymous"}
User Email: ${user?.email || "Not provided"}
Submitted: ${new Date().toISOString()}

Description:
${formData.description}

${formData.category === "bug" ? `
Steps to Reproduce:
${formData.steps}

Expected Behavior:
${formData.expectedBehavior}

Actual Behavior:
${formData.actualBehavior}
` : ""}

Browser/System Information:
${formData.browserInfo}

Additional Information:
${formData.additionalInfo}

---
This feedback was submitted through the gitRAG feedback form.
        `.trim()
      };

      // Here you would typically send to your backend API
      // For now, we'll simulate the email sending
      console.log("Feedback data:", emailData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSubmitted(true);
      setFormData({
        category: "bug",
        title: "",
        description: "",
        steps: "",
        expectedBehavior: "",
        actualBehavior: "",
        browserInfo: formData.browserInfo, // Keep browser info
        additionalInfo: "",
      });
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
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

        {/* Success Message */}
        <main className="flex flex-col flex-1 items-center justify-center bg-[#161b22] text-gray-200 p-4 sm:p-8 w-full">
          <div className="max-w-2xl w-full text-center">
            <div className="bg-[#21262d] border border-[#2ea04322] rounded-2xl p-8 shadow-lg">
              <CheckCircle size={64} className="text-[#2ea043] mx-auto mb-6" />
              <h1 className="text-3xl font-bold mb-4 text-[#2ea043]">Thank You!</h1>
              <p className="text-lg text-gray-300 mb-6">
                Your feedback has been successfully submitted. We appreciate you taking the time to help us improve gitRAG.
              </p>
              <p className="text-gray-400 mb-8">
                We'll review your feedback and get back to you if needed. Your input helps us make gitRAG better for everyone.
              </p>
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => setSubmitted(false)}
                  className="bg-[#2ea043] hover:bg-[#268839] px-6 py-3 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105"
                >
                  Submit Another Feedback
                </button>
                <a
                  href="/ai"
                  className="bg-[#21262d] hover:bg-[#2d333b] border border-[#2ea04322] px-6 py-3 rounded-lg font-semibold text-gray-200 transition-all duration-300 transform hover:scale-105"
                >
                  Back to AI Chat
                </a>
              </div>
            </div>
          </div>
        </main>
        <Footer user={user} />
      </div>
    );
  }

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

      {/* --- MAIN CONTENT --- */}
      <main className="flex flex-col flex-1 items-center bg-[#161b22] text-gray-200 p-4 sm:p-8 w-full">
        <div className="max-w-4xl w-full">
          {/* Header */}
          <div className="text-center mb-8 mt-8">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-6 text-[#2ea043] leading-tight">
              Help Us Improve gitRAG
            </h1>
            <p className="text-lg text-gray-300 mb-4">
              Found a bug? Have a feature request? We'd love to hear from you!
            </p>
            <p className="text-gray-400">
              Your feedback helps us build a better experience for everyone. Please provide as much detail as possible.
            </p>
          </div>

          {/* Feedback Categories */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {feedbackCategories.map((category, i) => (
              <div
                key={i}
                className={`bg-[#21262d] border border-[#2ea04322] rounded-2xl p-6 flex flex-col gap-4 shadow-md hover:shadow-[#2ea04333] transition-transform duration-300 hover:scale-105 group ${
                  formData.category === category.title.toLowerCase().replace(" ", "") ? "ring-2 ring-[#2ea043]" : ""
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`${category.bgColor} p-3 rounded-xl`}>
                    <category.icon size={26} className={category.color} />
                  </div>
                  <span className="font-bold text-lg text-gray-200">
                    {category.title}
                  </span>
                </div>
                <div className="text-gray-400 group-hover:text-gray-200 transition">
                  {category.description}
                </div>
              </div>
            ))}
          </div>

          {/* Feedback Form */}
          <div className="bg-[#21262d] border border-[#2ea04322] rounded-2xl p-8 shadow-lg">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Category Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Feedback Category *
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent"
                  required
                >
                  <option value="bug">Bug Report</option>
                  <option value="feature">Feature Request</option>
                  <option value="general">General Feedback</option>
                </select>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Brief description of your feedback"
                  className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Please provide a detailed description of your feedback"
                  className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent resize-vertical"
                  required
                />
              </div>

              {/* Bug-specific fields */}
              {formData.category === "bug" && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Steps to Reproduce
                    </label>
                    <textarea
                      name="steps"
                      value={formData.steps}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="1. Go to...&#10;2. Click on...&#10;3. See error..."
                      className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent resize-vertical"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Expected Behavior
                      </label>
                      <textarea
                        name="expectedBehavior"
                        value={formData.expectedBehavior}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="What should happen?"
                        className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent resize-vertical"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Actual Behavior
                      </label>
                      <textarea
                        name="actualBehavior"
                        value={formData.actualBehavior}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="What actually happens?"
                        className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent resize-vertical"
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Additional Information */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Additional Information
                </label>
                <textarea
                  name="additionalInfo"
                  value={formData.additionalInfo}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="Any additional context, screenshots, or information that might be helpful"
                  className="w-full bg-[#161b22] border border-[#2ea04322] rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#2ea043] focus:border-transparent resize-vertical"
                />
              </div>
              {/* Submit Button */}
              <div className="flex justify-center pt-4">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`bg-[#2ea043] hover:bg-[#268839] px-8 py-4 rounded-lg font-semibold text-lg text-white transition-all duration-300 transform hover:scale-105 flex items-center gap-3 shadow-lg shadow-[#2ea043]/30 ${
                    isSubmitting ? "opacity-50 cursor-not-allowed" : ""
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send size={20} />
                      Submit Feedback
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>

      {/* --- Footer --- */}
      <Footer user={user} />
    </div>
  );
}