type SuggestionCardProps = {
  label: string;
  onClick: () => void;
};

const SuggestionCard = ({ label, onClick }: SuggestionCardProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Ask: ${label}`}
      className="inline-flex items-center justify-center rounded-full border border-[#C7F0EA] bg-[#F0FDFA] px-4 py-2.5 text-sm font-medium text-[#0F766E] transition-colors duration-150 hover:border-[#7DD3C8] hover:bg-[#DFFBF4] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F8FAFC]"
    >
      {label}
    </button>
  );
};

export default SuggestionCard;
