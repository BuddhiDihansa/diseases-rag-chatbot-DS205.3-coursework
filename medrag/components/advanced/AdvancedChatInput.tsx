"use client";

import { useState } from "react";

interface AdvancedChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  canSend: boolean;
}

const AdvancedChatInput = ({
  value,
  onChange,
  onSubmit,
  canSend,
}: AdvancedChatInputProps) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (canSend) {
      onSubmit();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 border-t border-[#1E293B] bg-[#0F172A] px-4 py-4 sm:px-6"
    >
      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded-lg border border-[#1E293B] bg-[#1A1F35] px-2 py-1 text-xs font-medium text-[#64748B] transition-all hover:border-[#0F766E]/30 hover:bg-[#1E293B] hover:text-[#14B8A6]"
        >
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          Information
        </button>
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded-lg border border-[#1E293B] bg-[#1A1F35] px-2 py-1 text-xs font-medium text-[#64748B] transition-all hover:border-[#0F766E]/30 hover:bg-[#1E293B] hover:text-[#14B8A6]"
        >
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
          </svg>
          Symptoms
        </button>
      </div>

      {/* Input Field */}
      <div
        className={`flex transform items-center gap-2 rounded-xl border-2 bg-[#1A1F35] transition-all duration-200 ${
          isFocused
            ? "border-[#0F766E] bg-[#1E293B] shadow-lg shadow-[#0F766E]/10"
            : "border-[#1E293B]"
        }`}
      >
        <div className="flex-1">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Ask about symptoms, diseases, treatments..."
            className="w-full border-0 bg-transparent px-4 py-3 text-sm text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:ring-0"
          />
        </div>

        {value.trim() && (
          <button
            type="button"
            className="mr-2 rounded-lg p-2 text-[#64748B] transition-colors hover:bg-[#0F766E]/20 hover:text-[#14B8A6]"
            onClick={() => onChange("")}
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
            </svg>
          </button>
        )}

        <button
          type="submit"
          disabled={!canSend}
          className={`mr-2 inline-flex items-center justify-center rounded-lg px-4 py-2 font-semibold transition-all duration-200 ${
            canSend
              ? "bg-gradient-to-r from-[#0F766E] to-[#14B8A6] text-white shadow-lg hover:shadow-[#0F766E]/50 hover:from-[#115E59] hover:to-[#0D9488]"
              : "bg-[#1E293B] text-[#64748B]"
          }`}
        >
          <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16346272 C3.34915502,0.9 2.40734225,1.00636533 1.77946707,1.4776575 C0.994623095,2.10604706 0.837654326,3.0486314 1.15159189,3.98721575 L3.03521743,10.4282088 C3.03521743,10.5853061 3.19218622,10.7424035 3.50612381,10.7424035 L16.6915026,11.5278905 C16.6915026,11.5278905 17.1624089,11.5278905 17.1624089,12.0048122 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z" />
          </svg>
        </button>
      </div>

      <p className="text-xs text-[#64748B]">
        Press Enter to send • Powered by MedRAG AI
      </p>
    </form>
  );
};

export default AdvancedChatInput;
