"use client";

const LoadingIndicator = () => {
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
          <div className="flex items-center gap-2">
            <p className="text-sm text-[#64748B] sm:text-base">
              MedRAG is searching the medical knowledge base
            </p>
            <div className="flex gap-1">
              <span
                className="inline-block h-2 w-2 rounded-full bg-[#0F766E] opacity-75"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0s",
                }}
              />
              <span
                className="inline-block h-2 w-2 rounded-full bg-[#0F766E] opacity-75"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0.2s",
                }}
              />
              <span
                className="inline-block h-2 w-2 rounded-full bg-[#0F766E] opacity-75"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0.4s",
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%,
          60%,
          100% {
            opacity: 0.3;
          }
          30% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingIndicator;
