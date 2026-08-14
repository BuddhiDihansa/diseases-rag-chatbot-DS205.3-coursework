"use client";

import { useState, useRef, useEffect } from "react";
import AdvancedChatInput from "./AdvancedChatInput";
import AdvancedMessage from "./AdvancedMessage";
import AdvancedLoadingIndicator from "./AdvancedLoadingIndicator";
import AdvancedWelcome from "./AdvancedWelcome";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
}

interface AdvancedChatInterfaceProps {
  onNewChat: () => void;
}

const mockResponses: Record<string, string> = {
  "what is diabetes?":
    "Diabetes is a chronic metabolic disorder characterized by elevated blood glucose levels. The condition occurs when the pancreas cannot produce sufficient insulin or when the body cannot effectively utilize the insulin produced.\n\n• Type 1 Diabetes: Autoimmune condition where the body's immune system attacks insulin-producing beta cells in the pancreas\n• Type 2 Diabetes: Most common form accounting for 85-90% of cases, primarily due to insulin resistance and lifestyle factors\n• Gestational Diabetes: Occurs during pregnancy and usually resolves post-delivery\n• Secondary Diabetes: Results from other conditions such as pancreatitis or hemochromatosis\n\nCommon risk factors include family history, obesity, sedentary lifestyle, poor diet, and advancing age. Early detection and comprehensive management can significantly reduce complications.",
  "what are the symptoms of dengue?":
    "Dengue fever is a mosquito-borne viral infection with a typical incubation period of 3-14 days after the mosquito bite. The disease presents with a characteristic set of symptoms:\n\n• High fever (often reaching 40°C/104°F) that typically lasts 2-7 days\n• Severe headache, particularly behind the eyes (retro-orbital pain)\n• Intense muscle and joint pain (the reason it's called 'breakbone fever')\n• Characteristic maculopapular rash appearing after fever subsides\n• Nausea, vomiting, and loss of appetite\n• Minor hemorrhagic manifestations such as bleeding gums, nosebleeds\n\nThe majority of patients recover within 7-10 days. However, approximately 5% of cases progress to severe dengue (previously called dengue hemorrhagic fever), which requires immediate hospitalization and medical intervention.",
  "what causes asthma?":
    "Asthma is a chronic inflammatory disease of the airways characterized by reversible airflow obstruction, bronchial hyperresponsiveness, and inflammation. Multiple factors contribute to asthma development:\n\n• Genetic predisposition: Family history significantly increases risk\n• Environmental triggers: Allergens, air pollution, smoke exposure, weather changes\n• Respiratory infections: Viral upper respiratory infections can trigger or exacerbate asthma\n• Chronic airway inflammation: Leading to structural changes and hyperreactivity\n• Immune system dysregulation: Abnormal Th2-mediated immune response\n• Occupational exposures: Specific workplace irritants and allergens\n\nCommon triggers include dust mites, pet dander, pollen, exercise (exercise-induced asthma), stress, and sudden temperature changes. Proper management includes identifying and avoiding triggers, using inhaled corticosteroids, and having a rescue inhaler available.",
};

const AdvancedChatInterface = ({ onNewChat }: AdvancedChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const canSend = inputValue.trim().length > 0 && !isLoading;

  const generateMockResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase().trim();

    for (const [key, response] of Object.entries(mockResponses)) {
      if (lowerMessage.includes(key) || key.includes(lowerMessage)) {
        return response;
      }
    }

    return `**[MOCK RESPONSE - UI Testing Mode]**\n\nThis is a simulated response for UI testing. Your question: "${userMessage}"\n\nWhen connected to the backend, this will:\n• Search the medical knowledge base using semantic search\n• Retrieve relevant medical documents and guidelines\n• Rank results using cross-encoder reranking\n• Return evidence-based answers with credible sources`;
  };

  const handleSubmit = async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    await new Promise((resolve) => setTimeout(resolve, 2000));

    const assistantMessage: Message = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: generateMockResponse(trimmedInput),
      timestamp: new Date(),
      sources: [
        "MedicalNewsToday",
        "WHO Guidelines",
        "Clinical Research Database",
      ],
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInputValue("");
    setIsLoading(false);
    onNewChat();
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden bg-gradient-to-b from-[#0F172A] to-[#1A1F35]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {messages.length === 0 ? (
          <AdvancedWelcome onNewChat={handleNewChat} />
        ) : (
          <div className="mx-auto max-w-4xl space-y-6">
            {messages.map((message) => (
              <AdvancedMessage
                key={message.id}
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
                sources={message.sources}
              />
            ))}
            {isLoading && <AdvancedLoadingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="mx-auto w-full max-w-4xl">
        <AdvancedChatInput
          value={inputValue}
          onChange={setInputValue}
          onSubmit={handleSubmit}
          canSend={canSend}
        />
      </div>
    </div>
  );
};

export default AdvancedChatInterface;
