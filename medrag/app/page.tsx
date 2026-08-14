"use client";

import { useState, useCallback } from "react";
import ChatInterface from "@/components/ChatInterface";
import Header from "@/components/Header";

export default function Home() {
  const [hasMessages, setHasMessages] = useState(false);

  const handleNewChat = useCallback(() => {
    setHasMessages(false);
  }, []);

  const handleMessagesChange = useCallback((count: number) => {
    setHasMessages(count > 0);
  }, []);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      <Header hasMessages={hasMessages} onNewChat={handleNewChat} />
      <ChatInterface
        onMessagesChange={handleMessagesChange}
        onNewChat={handleNewChat}
      />
    </div>
  );
}
