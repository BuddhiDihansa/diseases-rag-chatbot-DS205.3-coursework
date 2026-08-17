"use client";

import type { ChatSession } from "@/lib/chatStore";
import { relativeTime } from "@/lib/chatStore";
import {
  ChatBubbleIcon,
  CloseIcon,
  MoonIcon,
  PlusIcon,
  PulseLogoIcon,
  SunIcon,
  TrashIcon,
} from "./icons";

type Theme = "light" | "dark";

export default function Sidebar({
  sessions,
  activeId,
  onSelect,
  onNew,
  onDelete,
  theme,
  onToggleTheme,
  mobileOpen,
  onCloseMobile,
}: {
  sessions: ChatSession[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  theme: Theme;
  onToggleTheme: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}) {
  const ordered = [...sessions].sort((a, b) => b.updatedAt - a.updatedAt);

  return (
    <>
      <div
        onClick={onCloseMobile}
        aria-hidden="true"
        className={`fixed inset-0 z-30 bg-black/40 transition-opacity duration-300 lg:hidden ${
          mobileOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        }`}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-[268px] shrink-0 -translate-x-full flex-col border-r border-sidebar-border bg-sidebar text-ink transition-transform duration-300 ease-out dark:border-navy-border dark:bg-navy dark:text-white lg:static lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : ""
        }`}
      >
        <div className="flex items-center justify-between gap-2 border-b border-sidebar-border px-5 py-4 dark:border-navy-border">
          <div className="flex items-center gap-2.5">
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary text-white">
              <PulseLogoIcon className="h-4 w-5" />
            </span>
            <div>
              <p className="font-display text-[15px] font-bold leading-tight text-ink dark:text-white">
                MediGuide LK
              </p>
              <p className="font-mono text-[9px] uppercase tracking-[0.25em] text-ink-soft/70 dark:text-white/40">
                Grounded copilot
              </p>
            </div>
          </div>
          <button
            onClick={onCloseMobile}
            aria-label="Close sidebar"
            className="rounded-lg p-1.5 text-ink-soft transition hover:bg-black/5 dark:text-white/60 dark:hover:bg-white/10 lg:hidden"
          >
            <CloseIcon className="h-4 w-4" />
          </button>
        </div>

        <div className="px-4 pt-4">
          <button
            onClick={onNew}
            className="group flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-[13.5px] font-semibold text-white transition-colors duration-150 hover:bg-primary-dark active:scale-[0.97]"
          >
            <PlusIcon className="h-4 w-4 transition-transform duration-200 group-active:rotate-90" />
            New chat
          </button>
        </div>

        <div className="scrollbar-thin mt-4 flex-1 space-y-0.5 overflow-y-auto px-3 pb-3">
          <p className="px-2 pb-1.5 font-mono text-[10px] uppercase tracking-[0.28em] text-ink-soft/60 dark:text-white/35">
            History
          </p>

          {ordered.length === 0 && (
            <p className="px-2 py-6 text-center text-[13px] leading-relaxed text-ink-soft/60 dark:text-white/35">
              Your conversations will appear here.
            </p>
          )}

          {ordered.map((session, index) => {
            const isActive = session.id === activeId;
            return (
              <div
                key={session.id}
                style={{ animationDelay: `${Math.min(index, 8) * 35}ms` }}
                className="animate-rise"
              >
                <button
                  onClick={() => onSelect(session.id)}
                  className={`group relative flex w-full items-center gap-2.5 overflow-hidden rounded-lg px-3 py-2.5 text-left transition-colors duration-150 ${
                    isActive
                      ? "bg-primary-soft text-ink dark:bg-primary/15 dark:text-white"
                      : "text-ink-soft hover:bg-black/[0.04] dark:text-white/60 dark:hover:bg-white/5"
                  }`}
                >
                  <span
                    className={`absolute left-0 top-1/2 h-[60%] w-[3px] -translate-y-1/2 rounded-r-full bg-primary transition-transform duration-300 ${
                      isActive ? "scale-y-100" : "scale-y-0"
                    }`}
                  />
                  <ChatBubbleIcon
                    className={`h-4 w-4 shrink-0 ${
                      isActive ? "text-primary" : "text-ink-soft/50 dark:text-white/30"
                    }`}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[13.5px] font-medium leading-tight">
                      {session.title}
                    </span>
                    <span className="mt-0.5 block font-mono text-[10.5px] text-ink-soft/50 dark:text-white/35">
                      {relativeTime(session.updatedAt)}
                    </span>
                  </span>
                  <span
                    onClick={(event) => {
                      event.stopPropagation();
                      onDelete(session.id);
                    }}
                    role="button"
                    aria-label="Delete conversation"
                    className="shrink-0 rounded-md p-1.5 text-ink-soft/0 transition-colors duration-150 hover:bg-rose/15 hover:text-rose group-hover:text-ink-soft/50 dark:group-hover:text-white/40"
                  >
                    <TrashIcon className="h-3.5 w-3.5" />
                  </span>
                </button>
              </div>
            );
          })}
        </div>

        <div className="border-t border-sidebar-border px-4 py-4 dark:border-navy-border">
          <button
            onClick={onToggleTheme}
            className="flex w-full items-center justify-between rounded-xl border border-sidebar-border bg-white/60 px-3.5 py-2.5 transition hover:border-primary/40 dark:border-navy-border dark:bg-white/[0.03] dark:hover:border-primary/40"
          >
            <span className="text-[13px] font-medium text-ink-soft dark:text-white/70">
              {theme === "dark" ? "Dark mode" : "Light mode"}
            </span>
            <span className="relative grid h-6 w-11 shrink-0 place-items-center rounded-full bg-black/10 dark:bg-white/15">
              <span
                className={`absolute left-0.5 grid h-5 w-5 place-items-center rounded-full bg-white shadow-md transition-transform duration-300 ease-out dark:bg-navy ${
                  theme === "dark" ? "translate-x-5" : "translate-x-0"
                }`}
              >
                <SunIcon
                  className={`absolute h-3 w-3 text-accent-dark transition-all duration-200 ${
                    theme === "dark" ? "scale-0 opacity-0 rotate-90" : "scale-100 opacity-100 rotate-0"
                  }`}
                />
                <MoonIcon
                  className={`absolute h-3 w-3 text-primary transition-all duration-200 ${
                    theme === "dark" ? "scale-100 opacity-100 rotate-0" : "scale-0 opacity-0 -rotate-90"
                  }`}
                />
              </span>
            </span>
          </button>
          <p className="mt-3 px-1 text-[10.5px] leading-relaxed text-ink-soft/60 dark:text-white/35">
            Informational only — not a substitute for professional medical advice.
          </p>
        </div>
      </aside>
    </>
  );
}