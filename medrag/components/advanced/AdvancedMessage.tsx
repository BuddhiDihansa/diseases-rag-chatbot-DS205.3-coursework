"use client";

interface AdvancedMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
}

const AdvancedMessage = ({
  role,
  content,
  timestamp,
  sources,
}: AdvancedMessageProps) => {
  if (role === "user") {
    return (
      <div className="flex justify-end">
        <div className="group max-w-md space-y-2">
          <div className="inline-block rounded-2xl bg-gradient-to-r from-[#0F766E] to-[#14B8A6] px-4 py-3 shadow-lg">
            <p className="text-sm leading-relaxed text-white">{content}</p>
          </div>
          <p className="px-2 text-right text-xs text-[#64748B]">
            {timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex gap-3">
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[#0F766E] to-[#14B8A6] shadow-lg">
        <svg
          className="h-5 w-5 text-white"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <path d="M12 3.5c2.5 0 4.5 2 4.5 4.5 0 2.1-1.5 3.7-3.5 4.2V18a1 1 0 0 1-2 0v-5.8C9 11.7 7.5 10.1 7.5 8c0-2.5 2-4.5 4.5-4.5Z" />
          <path d="M9.5 14.5h5" />
          <path d="M12 10.5v6" />
        </svg>
      </div>

      <div className="max-w-2xl space-y-3 flex-1">
        <div className="group rounded-2xl border border-[#1E293B] bg-[#1A1F35] p-4 shadow-lg transition-all hover:border-[#0F766E]/30">
          <div className="prose prose-invert prose-sm max-w-none text-sm leading-relaxed text-[#E2E8F0]">
            {content.split("\n\n").map((paragraph, idx) => {
              if (paragraph.startsWith("•") || paragraph.startsWith("-")) {
                const items = paragraph
                  .split("\n")
                  .filter((line) => line.trim().length > 0);
                return (
                  <ul key={idx} className="list-inside space-y-2">
                    {items.map((item, itemIdx) => (
                      <li key={itemIdx} className="flex gap-2">
                        <span className="text-[#14B8A6]">•</span>
                        <span>{item.replace(/^[•\-]\s*/, "")}</span>
                      </li>
                    ))}
                  </ul>
                );
              }

              return (
                <p key={idx} className="text-[#E2E8F0]">
                  {paragraph}
                </p>
              );
            })}
          </div>
        </div>

        {sources && sources.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <svg
                className="h-4 w-4 text-[#64748B]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              </svg>
              <p className="text-xs font-medium text-[#64748B]">Sources</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {sources.map((source, idx) => (
                <button
                  key={idx}
                  className="inline-flex items-center gap-1 rounded-full border border-[#0F766E]/30 bg-[#0F766E]/10 px-3 py-1 text-xs text-[#14B8A6] transition-all hover:border-[#0F766E]/60 hover:bg-[#0F766E]/20"
                >
                  <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="1" />
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {source}
                </button>
              ))}
            </div>
          </div>
        )}

        <p className="px-2 text-xs text-[#64748B]">
          {timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
};

export default AdvancedMessage;
