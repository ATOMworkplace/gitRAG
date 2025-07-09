import React from "react";
import { Github, Star, GitFork, Globe2, BadgeCheck, BookOpen } from "lucide-react";

export default function RepoPanel({ repoData, handleNewRepo }) {
  if (!repoData) return null;
  return (
    <div className="md:w-[25%] w-full bg-[#20252b] border border-[#232b36] rounded shadow-sm p-4 flex flex-col">
      <img src={repoData.avatar_url} alt="repo owner" className="w-14 h-14 rounded-full border-2 border-[#238636] shadow-sm mb-3 self-center" />
      <div className="flex-1">
        <div className="flex flex-wrap items-center gap-2 mb-1">
          <a href={repoData.html_url} target="_blank" rel="noopener noreferrer" className="text-lg font-bold text-[#2ea043] hover:underline flex items-center gap-1 truncate">
            <Github className="w-5 h-5" /> {repoData.name}
          </a>
          <span className="bg-[#2ea043]/20 text-[#2ea043] text-xs px-2 py-0.5 rounded">{repoData.owner}</span>
        </div>
        {repoData.homepage && (
          <a
            href={repoData.homepage}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-xs text-[#2ea043] hover:underline mb-1"
          >
            <Globe2 className="inline w-3 h-3 mr-1 -mt-0.5" />
            {repoData.homepage}
          </a>
        )}
        <div className="flex gap-4 text-gray-400 text-xs mb-1">
          <span className="flex items-center gap-1">
            <Star className="w-4 h-4" /> {repoData.stars}
          </span>
          <span className="flex items-center gap-1">
            <GitFork className="w-4 h-4" /> {repoData.forks}
          </span>
          {repoData.main_language && (
            <span className="flex items-center gap-1">
              <BookOpen className="w-4 h-4" /> {repoData.main_language}
            </span>
          )}
          {repoData.license && (
            <span className="flex items-center gap-1">
              <BadgeCheck className="w-4 h-4" /> {repoData.license}
            </span>
          )}
        </div>
        <div className="text-gray-300 text-sm mb-2 break-words">{repoData.description}</div>
        {repoData.topics && repoData.topics.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {repoData.topics.map((t) => (
              <span key={t} className="bg-[#232b36] border border-[#2ea043]/40 text-xs text-[#2ea043] px-2 py-0.5 rounded-full">{t}</span>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2 mt-1">
          <img src={repoData.profile.avatar_url} className="w-6 h-6 rounded-full border border-[#232b36]" alt="profile" />
          <a href={repoData.profile.github} target="_blank" rel="noopener noreferrer" className="text-xs font-semibold text-[#2ea043] hover:underline truncate">
            {repoData.profile.name}
          </a>
        </div>
      </div>
      <button
        className="flex items-center gap-2 px-4 py-2 bg-[#232b36] border border-[#232b36] rounded shadow text-sm text-[#2ea043] hover:bg-[#2ea043] hover:text-white transition font-semibold mt-6"
        onClick={handleNewRepo}
      >
        <Github className="w-4 h-4" />
        Close This Repo
      </button>
    </div>
  );
}
