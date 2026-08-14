"use client";

import RobotDoctor from "./RobotDoctor";

interface AdvancedHeaderProps {
  onMenuClick: () => void;
  sidebarOpen: boolean;
  onThemeToggle: () => void;
  theme: "dark" | "light";
}

const AdvancedHeader = ({
  onMenuClick,
  sidebarOpen,
  onThemeToggle,
  theme,
}: AdvancedHeaderProps) => {
  const isDark = theme === "dark";

  return (
    <header
      className={`border-b ${
        isDark
          ? "border-[#1E293B] bg-[#0F172A]/80"
          : "border-[#E2E8F0] bg-[#F8FAFC]/80"
      } backdrop-blur-md`}
    >
      <div className="flex items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className={`inline-flex items-center justify-center rounded-lg p-2 transition-colors lg:hidden ${
              isDark
                ? "text-[#64748B] hover:bg-[#1E293B] hover:text-[#E2E8F0]"
                : "text-[#64748B] hover:bg-[#E2E8F0] hover:text-[#0F172A]"
            }`}
            aria-label="Toggle sidebar"
          >
            <svg
              className="h-6 w-6"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <div className="flex items-center gap-2">
            <RobotDoctor />
            <div>
              <p
                className={`text-sm font-semibold ${
                  isDark ? "text-[#E2E8F0]" : "text-[#0F172A]"
                }`}
              >
                MedRAG
              </p>
              <p
                className={`text-xs ${
                  isDark ? "text-[#64748B]" : "text-[#94A3B8]"
                }`}
              >
                Medical AI Assistant
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onThemeToggle}
            className={`inline-flex items-center justify-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
              isDark
                ? "border-[#1E293B] bg-[#1A1F35] text-[#64748B] hover:border-[#0F766E]/30 hover:bg-[#1E293B] hover:text-[#14B8A6]"
                : "border-[#E2E8F0] bg-white text-[#0F172A] hover:border-[#0F766E] hover:text-[#0F766E]"
            }`}
            aria-label="Toggle theme"
            title={`Switch to ${isDark ? "light" : "dark"} mode`}
          >
            {isDark ? (
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 3v1m0 16v1m9-9h-1m-16 0H1m15.364 1.364l-.707.707M6.343 6.343l-.707-.707m12.728 0l-.707.707m-12.02 12.02l-.707.707M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M21.64 15.95c-.181-.765-.717-1.424-1.45-1.773-.732-.35-1.704-.226-2.476.524-.772.75-.972 1.645-.215 2.553.756.908.545 1.046.141 1.49-.404.444-.926.681-1.597.681-.566 0-1.107-.175-1.518-.475-1.4-.993-1.645-2.798-.504-4.226.717-.904 1.918-1.284 3.126-1.284 2.523 0 4.313 2.212 4.313 4.41 0 .667-.092 1.294-.266 1.9z" />
              </svg>
            )}
            <span className="hidden sm:inline">
              {isDark ? "Light" : "Dark"}
            </span>
          </button>

          <button
            className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
              isDark
                ? "border-[#1E293B] bg-[#1A1F35] text-[#64748B] hover:border-[#0F766E]/30 hover:bg-[#1E293B] hover:text-[#14B8A6]"
                : "border-[#E2E8F0] bg-white text-[#0F172A] hover:border-[#0F766E] hover:text-[#0F766E]"
            }`}
          >
            Upgrade
          </button>
        </div>
      </div>
    </header>
  );
};

export default AdvancedHeader;
