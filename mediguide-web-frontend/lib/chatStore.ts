import type { ChatResponse } from "./api";

export type ChatMessage =
  | { role: "user"; content: string; id: string }
  | {
      role: "assistant";
      content: string;
      id: string;
      meta?: ChatResponse;
      error?: string;
    };

export type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
  updatedAt: number;
};

const SESSIONS_KEY = "mediguide-sessions-v1";
const ACTIVE_KEY = "mediguide-active-session-v1";
export const THEME_KEY = "mediguide-theme";

export function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export function createSession(): ChatSession {
  return {
    id: uid(),
    title: "New conversation",
    messages: [],
    updatedAt: Date.now(),
  };
}

export function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as ChatSession[]) : [];
  } catch {
    return [];
  }
}

export function saveSessions(sessions: ChatSession[]) {
  try {
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
  } catch {
    // Ignore persistence failures (private mode, quota, etc.)
  }
}

export function loadActiveId(): string | null {
  try {
    return localStorage.getItem(ACTIVE_KEY);
  } catch {
    return null;
  }
}

export function saveActiveId(id: string) {
  try {
    localStorage.setItem(ACTIVE_KEY, id);
  } catch {
    // Ignore persistence failures.
  }
}

export function deriveTitle(messages: ChatMessage[]): string {
  const firstUser = messages.find((message) => message.role === "user");
  if (!firstUser || !firstUser.content.trim()) return "New conversation";
  const text = firstUser.content.trim().replace(/\s+/g, " ");
  return text.length > 42 ? `${text.slice(0, 42)}…` : text;
}

export function relativeTime(timestamp: number): string {
  const diffMs = Date.now() - timestamp;
  const minute = 60000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diffMs < minute) return "Just now";
  if (diffMs < hour) return `${Math.floor(diffMs / minute)}m ago`;
  if (diffMs < day) return `${Math.floor(diffMs / hour)}h ago`;
  if (diffMs < 7 * day) return `${Math.floor(diffMs / day)}d ago`;
  return new Date(timestamp).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}