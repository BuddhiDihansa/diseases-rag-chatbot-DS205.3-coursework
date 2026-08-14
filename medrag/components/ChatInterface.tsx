"use client";

import { useState, useRef, useEffect } from "react";
import ChatInput from "./ChatInput";
import EmptyState from "./EmptyState";
import SuggestionCard from "./SuggestionCard";
import Message, { Message as MessageType } from "./Message";
import LoadingIndicator from "./LoadingIndicator";

const suggestions = [
  "What is diabetes?",
  "What are the symptoms of dengue?",
  "What causes asthma?",
];

// Mock assistant responses for testing
const mockResponses: Record<string, string> = {
  "what is diabetes?":
    "Diabetes is a chronic metabolic disorder characterized by high blood sugar levels. It occurs when the pancreas cannot produce enough insulin or when the body cannot effectively use the insulin produced.\n\n• Type 1: Autoimmune condition where the pancreas produces little or no insulin\n• Type 2: Most common form where the body develops insulin resistance\n• Gestational: Occurs during pregnancy and usually resolves after delivery\n\nKey risk factors include family history, obesity, sedentary lifestyle, and age. Early detection and management can prevent serious complications.",
  "what are the symptoms of dengue?":
    "Dengue fever symptoms typically appear 3-14 days after infection. Common symptoms include:\n\n• High fever (often reaching 40°C/104°F)\n• Severe headache and pain behind the eyes\n• Muscle and joint pain (hence the name 'breakbone fever')\n• Rash that typically appears after fever subsides\n• Nausea and vomiting\n• Mild bleeding (gums, nose)\n\nMost people recover within 7-10 days. Severe dengue can lead to dengue hemorrhagic fever, which requires immediate medical attention.",
  "what causes asthma?":
    "Asthma is a chronic respiratory condition that affects the airways in the lungs. Multiple factors contribute to asthma development:\n\n• Genetic factors: Family history significantly increases risk\n• Environmental triggers: Allergens, pollution, smoke, cold air\n• Respiratory infections: Viral infections can trigger or worsen asthma\n• Inflammation: Chronic airway inflammation narrows airways\n• Immune system response: Exaggerated response to irritants\n\nCommon triggers include dust mites, pet dander, pollen, exercise, stress, and weather changes. Proper management includes avoiding triggers and using prescribed medications.",
};

interface ChatInterfaceProps {
  onMessagesChange?: (count: number) => void;
  onNewChat?: () => void;
}

const ChatInterface = ({ onMessagesChange, onNewChat }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    onMessagesChange?.(messages.length);
  }, [messages, onMessagesChange]);

  const canSend = inputValue.trim().length > 0 && !isLoading;

  const generateMockResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase().trim();

    // Check for exact or partial match
    for (const [key, response] of Object.entries(mockResponses)) {
      if (lowerMessage.includes(key) || key.includes(lowerMessage)) {
        return response;
      }
    }

    // Default mock response
    return `**[MOCK RESPONSE - Not connected to backend]**\n\nThis is a simulated response for UI testing purposes. The actual backend is not connected yet.\n\nYour question: "${userMessage}"\n\nWhen connected to the backend, this will:\n• Search the medical knowledge base\n• Retrieve relevant medical documents\n• Return evidence-based answers with sources`;
  };

  const handleSubmit = async () => {
    const trimmedInput = inputValue.trim();
    await handleSubmitWithValue(trimmedInput);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    // Use setTimeout to ensure state is updated before submitting
    setTimeout(() => {
      handleSubmitWithValue(suggestion);
    }, 0);
  };

  const handleSubmitWithValue = async (value: string) => {
    const trimmedInput = value.trim();
    if (!trimmedInput || isLoading) return;

    // Add user message
    const userMessage: MessageType = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Add assistant response
    const assistantMessage: MessageType = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: generateMockResponse(trimmedInput),
      timestamp: new Date(),
      sources: [
        "Medical Knowledge Base",
        "Clinical Guidelines",
        "Research Database",
      ],
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInputValue("");
    setIsLoading(false);
    onNewChat?.();
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-[#F8FAFC] text-[#0F172A]">
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 pb-6 pt-0 sm:px-6 lg:px-8">
        {!hasMessages ? (
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
        ) : (
          <section className="flex flex-1 flex-col gap-6 overflow-y-auto py-6">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            {isLoading && <LoadingIndicator />}
            <div ref={messagesEndRef} />
          </section>
        )}

        <div className="mx-auto w-full max-w-3xl">
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
