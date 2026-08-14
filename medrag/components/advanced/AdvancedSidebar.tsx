"use client";

import { useState } from "react";

interface AdvancedSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: Array<{ id: string; title: string; timestamp: Date }>;
}

const AdvancedSidebar = ({
  isOpen,
  onClose,
  conversations,
}: AdvancedSidebarProps) => {
  const [newChatHovered, setNewChatHovered] = useState(false);

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r border-[#1E293B] bg-gradient-to-b from-[#0F172A] to-[#1A1F35] transition-transform duration-300 ease-in-out lg:static lg:z-0 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col overflow-hidden">
          {/* Header */}
          <div className="border-b border-[#1E293B] p-4">
            <button
              onClick={() => {}}
              className="group flex w-full items-center justify-center gap-2 rounded-lg border border-[#0F766E]/30 bg-gradient-to-r from-[#0F766E]/10 to-[#14B8A6]/10 px-4 py-3 text-sm font-semibold text-[#14B8A6] transition-all hover:border-[#0F766E]/60 hover:bg-gradient-to-r hover:from-[#0F766E]/20 hover:to-[#14B8A6]/20"
              onMouseEnter={() => setNewChatHovered(true)}
              onMouseLeave={() => setNewChatHovered(false)}
            >
              <svg
                className={`h-5 w-5 transition-transform duration-300 ${newChatHovered ? "scale-110 rotate-90" : ""}`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M12 5v14M5 12h14" />
              </svg>
              New Chat
            </button>
          </div>

          {/* Conversations */}
          <div className="flex-1 overflow-y-auto px-3 py-4">
            {conversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <svg
                  className="mb-3 h-8 w-8 text-[#64748B]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p className="text-sm text-[#64748B]">No conversations yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    className="group flex w-full flex-col gap-1 rounded-lg border border-transparent bg-[#1A1F35] px-3 py-2.5 text-left transition-all hover:border-[#0F766E]/30 hover:bg-[#1E293B]"
                  >
                    <p className="truncate text-sm font-medium text-[#E2E8F0] group-hover:text-[#14B8A6]">
                      {conv.title}
                    </p>
                    <p className="text-xs text-[#64748B]">
                      {conv.timestamp.toLocaleDateString()}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-[#1E293B] p-4">
            <button className="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-[#64748B] transition-colors hover:bg-[#1E293B] hover:text-[#E2E8F0]">
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="1" />
                <circle cx="19" cy="12" r="1" />
                <circle cx="5" cy="12" r="1" />
              </svg>
              Settings
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default AdvancedSidebar;
