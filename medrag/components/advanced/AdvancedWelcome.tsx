"use client";

interface AdvancedWelcomeProps {
  onNewChat: () => void;
}

const suggestions = [
  {
    title: "What is diabetes?",
    description: "Learn about diabetes types, symptoms, and management",
    icon: "M12 3.5c2.5 0 4.5 2 4.5 4.5 0 2.1-1.5 3.7-3.5 4.2V18a1 1 0 0 1-2 0v-5.8C9 11.7 7.5 10.1 7.5 8c0-2.5 2-4.5 4.5-4.5Z",
  },
  {
    title: "What are the symptoms of dengue?",
    description: "Understand dengue fever symptoms and prevention",
    icon: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z",
  },
  {
    title: "What causes asthma?",
    description: "Explore asthma triggers and treatment options",
    icon: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 9.5c0 .83-.67 1.5-1.5 1.5S11 13.33 11 12.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5z",
  },
];

const AdvancedWelcome = ({ onNewChat }: AdvancedWelcomeProps) => {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center justify-center">
      <div className="mb-8 text-center">
        <div className="mb-6 inline-flex items-center justify-center rounded-2xl bg-gradient-to-br from-[#0F766E]/20 to-[#14B8A6]/20 p-4">
          <svg
            className="h-12 w-12 text-[#14B8A6]"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <path d="M12 3.5c2.5 0 4.5 2 4.5 4.5 0 2.1-1.5 3.7-3.5 4.2V18a1 1 0 0 1-2 0v-5.8C9 11.7 7.5 10.1 7.5 8c0-2.5 2-4.5 4.5-4.5Z" />
            <path d="M9.5 14.5h5" />
            <path d="M12 10.5v6" />
          </svg>
        </div>

        <h1 className="mb-2 text-3xl font-bold text-[#E2E8F0] sm:text-4xl">
          Welcome to MedRAG
        </h1>
        <p className="text-lg text-[#64748B]">Advanced Medical AI Assistant</p>
        <p className="mt-3 text-sm text-[#94A3B8]">
          Ask questions about diseases, symptoms, treatments, and prevention.
          Powered by advanced AI and medical knowledge base.
        </p>
      </div>

      <div className="w-full space-y-3">
        <p className="text-sm font-medium text-[#94A3B8]">Explore topics:</p>
        <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-3">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={onNewChat}
              className="group flex flex-col gap-2 rounded-xl border border-[#1E293B] bg-[#1A1F35] p-4 text-left transition-all hover:border-[#0F766E]/60 hover:bg-[#1E293B]"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-[#E2E8F0] group-hover:text-[#14B8A6]">
                    {suggestion.title}
                  </p>
                  <p className="mt-1 text-xs text-[#64748B]">
                    {suggestion.description}
                  </p>
                </div>
                <svg
                  className="h-5 w-5 text-[#0F766E] opacity-0 transition-all group-hover:translate-x-1 group-hover:opacity-100"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="mt-8 rounded-xl border border-[#1E293B] bg-[#1A1F35]/50 p-4">
        <div className="flex gap-3">
          <svg
            className="h-5 w-5 shrink-0 text-[#14B8A6]"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          <div className="text-sm text-[#94A3B8]">
            <p className="font-medium text-[#E2E8F0]">Medical AI Assistant</p>
            <p className="mt-1">
              Provides evidence-based information sourced from medical knowledge
              base. Always consult healthcare professionals for diagnosis.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedWelcome;
