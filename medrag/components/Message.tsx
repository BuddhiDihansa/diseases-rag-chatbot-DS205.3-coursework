"use client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
}

interface MessageProps {
  message: Message;
}

const Message = ({ message }: MessageProps) => {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-xs rounded-2xl bg-[#E6FFFB] px-4 py-3 text-right sm:max-w-md md:max-w-lg">
          <p className="text-sm leading-relaxed text-[#0F172A] sm:text-base">
            {message.content}
          </p>
          <p className="mt-1 text-xs text-[#64748B]">
            {new Date(message.timestamp).toLocaleTimeString([], {
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
    <div className="flex justify-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[#DDE7E5] bg-white text-[#0F766E] shadow-sm">
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

      <div className="max-w-xs space-y-3 sm:max-w-md md:max-w-2xl">
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-4 shadow-sm">
          <div className="prose prose-sm max-w-none text-sm leading-relaxed text-[#0F172A] sm:text-base sm:prose-base">
            {message.content.split("\n\n").map((paragraph, idx) => {
              // Check if this paragraph is a bullet point list
              if (paragraph.startsWith("•") || paragraph.startsWith("-")) {
                const items = paragraph
                  .split("\n")
                  .filter((line) => line.trim().length > 0);
                return (
                  <ul key={idx} className="list-inside space-y-2 text-[#0F172A]">
                    {items.map((item, itemIdx) => (
                      <li key={itemIdx} className="flex gap-2">
                        <span className="text-[#0F766E]">•</span>
                        <span>{item.replace(/^[•\-]\s*/, "")}</span>
                      </li>
                    ))}
                  </ul>
                );
              }

              // Regular paragraph
              return (
                <p key={idx} className="text-[#0F172A]">
                  {paragraph}
                </p>
              );
            })}
          </div>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-[#64748B]">Sources:</p>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((source, idx) => (
                <span
                  key={idx}
                  className="inline-block rounded-full border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-1.5 text-xs text-[#64748B]"
                >
                  {source}
                </span>
              ))}
            </div>
          </div>
        )}

        <p className="text-xs text-[#64748B]">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
};

export default Message;
export type { Message };
