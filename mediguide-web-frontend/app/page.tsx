"use client";

import { useEffect, useState } from "react";
import Chat from "@/components/Chat";
import Sidebar from "@/components/Sidebar";
import DoctorRobot from "@/components/DoctorRobot";
import {
  THEME_KEY,
  createSession,
  deriveTitle,
  loadActiveId,
  loadSessions,
  saveActiveId,
  saveSessions,
  type ChatMessage,
  type ChatSession,
} from "@/lib/chatStore";

type Theme = "light" | "dark";

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [theme, setTheme] = useState<Theme>("light");
  const [hydrated, setHydrated] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    try {
      const storedTheme = localStorage.getItem(THEME_KEY);
      if (storedTheme === "dark" || storedTheme === "light") {
        setTheme(storedTheme);
        document.documentElement.classList.toggle("dark", storedTheme === "dark");
      }

      const storedSessions = loadSessions();
      const storedActive = loadActiveId();

      if (storedSessions.length > 0) {
        setSessions(storedSessions);
        const activeExists = storedSessions.some((s) => s.id === storedActive);
        setActiveId(activeExists ? storedActive : storedSessions[0].id);
      } else {
        const first = createSession();
        setSessions([first]);
        setActiveId(first.id);
      }
    } catch {
      const first = createSession();
      setSessions([first]);
      setActiveId(first.id);
    } finally {
      setHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    saveSessions(sessions);
  }, [sessions, hydrated]);

  useEffect(() => {
    if (!hydrated || !activeId) return;
    saveActiveId(activeId);
  }, [activeId, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    try {
      localStorage.setItem(THEME_KEY, theme);
      document.documentElement.classList.toggle("dark", theme === "dark");
      document.documentElement.dataset.theme = theme;
    } catch {
      // Ignore persistence failures.
    }
  }, [theme, hydrated]);

  function handleNewSession() {
    const fresh = createSession();
    setSessions((current) => [fresh, ...current]);
    setActiveId(fresh.id);
    setMobileOpen(false);
  }

  function handleSelectSession(id: string) {
    setActiveId(id);
    setMobileOpen(false);
  }

  function handleDeleteSession(id: string) {
    const remaining = sessions.filter((s) => s.id !== id);

    if (remaining.length > 0) {
      setSessions(remaining);
      if (id === activeId) {
        setActiveId(remaining[0].id);
      }
    } else {
      const fresh = createSession();
      setSessions([fresh]);
      setActiveId(fresh.id);
    }
  }

  function handleMessagesChange(messages: ChatMessage[]) {
    if (!activeId) return;
    setSessions((current) =>
      current.map((session) =>
        session.id === activeId
          ? { ...session, messages, title: deriveTitle(messages), updatedAt: Date.now() }
          : session
      )
    );
  }

  const activeSession = sessions.find((s) => s.id === activeId) ?? sessions[0];

  if (!hydrated || !activeSession) {
    return <main className="min-h-screen bg-paper dark:bg-navy" />;
  }

  return (
    <main className="relative flex min-h-screen overflow-hidden bg-paper dark:bg-navy">
      <DoctorRobot />

      <Sidebar
        sessions={sessions}
        activeId={activeSession.id}
        onSelect={handleSelectSession}
        onNew={handleNewSession}
        onDelete={handleDeleteSession}
        theme={theme}
        onToggleTheme={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <Chat
        key={activeSession.id}
        session={activeSession}
        onMessagesChange={handleMessagesChange}
        theme={theme}
        onToggleTheme={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
        onOpenSidebar={() => setMobileOpen(true)}
      />
    </main>
  );
}