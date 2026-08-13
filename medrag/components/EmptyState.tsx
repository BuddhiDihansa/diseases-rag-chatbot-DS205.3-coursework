const EmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-[#DDE7E5] bg-white text-[#0F766E] shadow-sm sm:h-20 sm:w-20">
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="h-8 w-8 sm:h-10 sm:w-10"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 4.5c-3 0-5.5 2.4-5.5 5.5 0 2.8 2 4.9 4.4 5.7v2.8a1 1 0 0 0 2 0v-2.8c2.4-.8 4.4-2.9 4.4-5.7 0-3.1-2.5-5.5-5.5-5.5Z" />
          <path d="M9.5 10.5h5M12 8v5" />
        </svg>
      </div>

      <div className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight text-[#0F172A] sm:text-4xl">
          MedRAG
        </h1>
        <p className="text-base font-medium text-[#0F766E] sm:text-lg">
          Medical Knowledge Assistant
        </p>
      </div>

      <p className="mt-4 max-w-xl text-sm leading-6 text-[#64748B] sm:text-base">
        Ask questions about diseases, symptoms, causes, diagnosis and prevention.
      </p>
    </div>
  );
};

export default EmptyState;
