type ChatInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  canSend: boolean;
};

const ChatInput = ({ value, onChange, onSubmit, canSend }: ChatInputProps) => {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!canSend) {
      return;
    }

    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-center gap-3 rounded-2xl border border-[#E2E8F0] bg-white px-3 py-2.5 shadow-sm transition-all duration-150 focus-within:border-[#0D9488] focus-within:ring-4 focus-within:ring-[#CCFBF1] sm:px-4">
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Ask a medical question..."
          aria-label="Ask a medical question"
          className="w-full border-0 bg-transparent px-1 py-2 text-sm text-[#0F172A] placeholder:text-[#94A3B8] focus:outline-none focus:ring-0 sm:text-base"
        />

        <button
          type="submit"
          disabled={!canSend}
          aria-label="Send message"
          className="inline-flex h-11 shrink-0 items-center justify-center rounded-xl bg-[#0F766E] px-4 text-sm font-semibold text-white transition-colors duration-150 hover:bg-[#115E59] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-[#CBD5E1] disabled:text-[#F8FAFC]"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
