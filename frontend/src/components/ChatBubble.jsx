import React from "react";
import ReactMarkdown from "react-markdown";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import js from "react-syntax-highlighter/dist/esm/languages/hljs/javascript";
import py from "react-syntax-highlighter/dist/esm/languages/hljs/python";
import cpp from "react-syntax-highlighter/dist/esm/languages/hljs/cpp";
import java from "react-syntax-highlighter/dist/esm/languages/hljs/java";
import atomOneDark from "react-syntax-highlighter/dist/esm/styles/hljs/atom-one-dark";
import { Trash2 } from "lucide-react";

// Register languages (only once!)
SyntaxHighlighter.registerLanguage("javascript", js);
SyntaxHighlighter.registerLanguage("python", py);
SyntaxHighlighter.registerLanguage("cpp", cpp);
SyntaxHighlighter.registerLanguage("java", java);

function detectLanguage(code = "") {
  if (/^\s*#include|std::|using\s+namespace\s+std/.test(code)) return "cpp";
  if (/^\s*import\s+\w+|def\s+\w+/.test(code) || /print\(.+\)/.test(code)) return "python";
  if (/^\s*public\s+class|System\.out\.println/.test(code)) return "java";
  if (/function\s*\(|const\s+\w+\s*=/.test(code) || /console\.log/.test(code)) return "javascript";
  return "text"; // fallback
}

export default function ChatBubble({ sender, text, avatar, onDelete, canDelete, id }) {
  const isUser = sender === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 group`}>
      {!isUser && (
        <img src={avatar || "/logo.png"} className="h-8 w-8 rounded-full mr-2 mt-1 shadow flex-shrink-0" alt="ai" />
      )}
      <div
        className={`
          relative px-4 py-3 rounded-2xl max-w-[70vw] min-w-[90px]
          ${isUser
            ? "bg-[#2ea043] text-white rounded-br-md"
            : "bg-[#232b36] text-gray-200 border border-[#21262d] rounded-bl-md"}
        `}
        style={{
          wordBreak: "break-word",
          width: "fit-content",
          boxShadow: "0 2px 10px rgba(0,0,0,0.3)"
        }}
      >
        {canDelete && (
          <button
            className={`absolute top-1 ${isUser ? "right-1" : "left-1"} opacity-0 group-hover:opacity-80 transition-opacity rounded-full p-1 bg-black/40 hover:bg-red-600 text-white`}
            title="Delete"
            style={{ zIndex: 5 }}
            onClick={() => onDelete(id)}
          >
            <Trash2 size={16} />
          </button>
        )}
        <ReactMarkdown
          components={{
            strong: ({ node, ...props }) => <b className="font-semibold text-[#ffd700]" {...props} />,
            ul: ({ node, ...props }) => <ul className="list-disc ml-6 mb-3 mt-2" {...props} />,
            ol: ({ node, ...props }) => <ol className="list-decimal ml-6 mb-3 mt-2" {...props} />,
            li: ({ node, ...props }) => <li className="mb-1" {...props} />,
            h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-3 mt-4" {...props} />,
            h2: ({ node, ...props }) => <h2 className="text-lg font-bold mb-2 mt-3" {...props} />,
            h3: ({ node, ...props }) => <h3 className="text-base font-bold mb-2 mt-3" {...props} />,
            blockquote: ({ node, ...props }) => (
              <blockquote className="border-l-4 border-[#2ea043] pl-4 italic mb-3 mt-2" {...props} />
            ),
            code({ node, inline, className, children, ...props }) {
              const code = String(children).replace(/\n$/, "");
              const lang = (className || "").replace("language-", "") || detectLanguage(code);
              
              if (inline) {
                return (
                  <code className="bg-[#1a2027] px-2 py-1 rounded text-[#61dafb] font-mono text-sm border border-[#2d3748]" {...props}>
                    {children}
                  </code>
                );
              }
              
              return (
                <div className="my-4">
                  <SyntaxHighlighter
                    style={atomOneDark}
                    language={lang}
                    customStyle={{
                      background: "#1e2029",
                      borderRadius: "0.5rem",
                      padding: "1rem",
                      fontSize: "0.9em",
                      border: "1px solid #2d3748",
                      margin: "0"
                    }}
                    PreTag="div"
                    showLineNumbers={true}
                    lineNumberStyle={{
                      color: "#6b7280",
                      fontSize: "0.8em",
                      paddingRight: "1em"
                    }}
                  >
                    {code}
                  </SyntaxHighlighter>
                </div>
              );
            },
            pre: ({ node, ...props }) => <div {...props} className="my-4" />,
            p: ({ node, ...props }) => <p className="mb-3 last:mb-0 leading-relaxed" {...props} />,
            a: ({ node, ...props }) => (
              <a 
                className="text-[#2ea043] underline hover:text-[#238636] transition-colors break-all" 
                target="_blank" 
                rel="noopener noreferrer" 
                {...props} 
              />
            ),
            hr: ({ node, ...props }) => <hr className="border-[#21262d] my-4" {...props} />,
            table: ({ node, ...props }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-[#21262d]" {...props} />
              </div>
            ),
            th: ({ node, ...props }) => (
              <th className="border border-[#21262d] px-3 py-2 bg-[#1a1e23] font-semibold text-left" {...props} />
            ),
            td: ({ node, ...props }) => (
              <td className="border border-[#21262d] px-3 py-2" {...props} />
            ),
          }}
        >
          {text}
        </ReactMarkdown>
      </div>
      {isUser && (
        <img src={avatar || "/logo.png"} className="h-8 w-8 rounded-full ml-2 mt-1 shadow flex-shrink-0" alt="user" />
      )}
    </div>
  );
}