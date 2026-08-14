"use client";

interface HeaderProps {
  hasMessages: boolean;
  onNewChat: () => void;
}

const Header = ({ hasMessages, onNewChat }: HeaderProps) => {
  return (
    <header className="w-full border-b border-[#E2E8F0] bg-[#F8FAFC]/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#DDE7E5] bg-white text-[#0F766E] shadow-sm">
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 3.5c2.5 0 4.5 2 4.5 4.5 0 2.1-1.5 3.7-3.5 4.2V18a1 1 0 0 1-2 0v-5.8C9 11.7 7.5 10.1 7.5 8c0-2.5 2-4.5 4.5-4.5Z" />
              <path d="M9.5 14.5h5" />
              <path d="M12 10.5v6" />
            </svg>
          </div>

          <div className="min-w-0">
            <p className="truncate text-base font-semibold tracking-tight text-[#0F172A] sm:text-lg">
              MedRAG
            </p>
            <p className="truncate text-[10px] font-medium uppercase tracking-[0.12em] text-[#64748B] sm:text-[11px]">
              Medical Knowledge Assistant
            </p>
          </div>
        </div>

        {hasMessages && (
          <button
            type="button"
            onClick={onNewChat}
            aria-label="Start a new chat"
            className="inline-flex items-center justify-center gap-2 rounded-full border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-medium text-[#0F172A] transition-colors hover:border-[#0F766E] hover:text-[#0F766E] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0F766E] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F8FAFC]"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
            <span className="hidden sm:inline">New Chat</span>
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
