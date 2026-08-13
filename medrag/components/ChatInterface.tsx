"use client";

import { useState } from "react";
import ChatInput from "./ChatInput";
import EmptyState from "./EmptyState";
import SuggestionCard from "./SuggestionCard";

const suggestions = [
  "What is diabetes?",
  "What are the symptoms of dengue?",
  "What causes asthma?",
];

const ChatInterface = () => {
  const [inputValue, setInputValue] = useState("");

  const canSend = inputValue.trim().length > 0;

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const handleSubmit = () => {
    setInputValue("");
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#F8FAFC] text-[#0F172A]">
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 pb-6 pt-0 sm:px-6 lg:px-8">
        <section className="flex flex-1 flex-col justify-center py-8 sm:py-12">
          <div className="mx-auto flex w-full max-w-3xl flex-col items-center justify-center">
            <EmptyState />

            <div className="mt-8 flex w-full flex-wrap items-center justify-center gap-3">
              {suggestions.map((suggestion) => (
                <SuggestionCard
                  key={suggestion}
                  label={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                />
              ))}
            </div>
          </div>
        </section>

        <div className="mx-auto w-full max-w-3xl pb-2">
          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSubmit}
            canSend={canSend}
          />
        </div>
      </main>
    </div>
  );
};

export default ChatInterface;
