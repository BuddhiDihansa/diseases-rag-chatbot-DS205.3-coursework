"use client";

import { useState } from "react";
import AdvancedChatInterface from "@/components/advanced/AdvancedChatInterface";
import AdvancedSidebar from "@/components/advanced/AdvancedSidebar";
import AdvancedHeader from "@/components/advanced/AdvancedHeader";

export default function AdvancedPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [conversationHistory, setConversationHistory] = useState<
    Array<{ id: string; title: string; timestamp: Date }>
  >([]);

  const handleNewChat = () => {
    setSidebarOpen(true);
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const isDark = theme === "dark";
  const bgColor = isDark ? "bg-[#0F172A]" : "bg-[#F8FAFC]";

  return (
    <div className={`flex h-screen overflow-hidden ${bgColor}`}>
      {/* Sidebar */}
      <AdvancedSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversationHistory}
        theme={theme}
      />

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <AdvancedHeader
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
          onThemeToggle={toggleTheme}
          theme={theme}
        />

        <AdvancedChatInterface onNewChat={handleNewChat} theme={theme} />
      </div>
    </div>
  );
}
