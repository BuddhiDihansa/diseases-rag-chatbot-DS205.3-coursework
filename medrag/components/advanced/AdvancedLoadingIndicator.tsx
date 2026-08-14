"use client";

const AdvancedLoadingIndicator = () => {
  return (
    <div className="flex gap-3">
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[#0F766E] to-[#14B8A6] shadow-lg">
        <svg
          className="h-5 w-5 text-white"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <path d="M12 3.5c2.5 0 4.5 2 4.5 4.5 0 2.1-1.5 3.7-3.5 4.2V18a1 1 0 0 1-2 0v-5.8C9 11.7 7.5 10.1 7.5 8c0-2.5 2-4.5 4.5-4.5Z" />
          <path d="M9.5 14.5h5" />
          <path d="M12 10.5v6" />
        </svg>
      </div>

      <div className="max-w-2xl flex-1">
        <div className="rounded-2xl border border-[#1E293B] bg-[#1A1F35] p-4 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div
                className="h-2 w-2 rounded-full bg-[#14B8A6]"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0s",
                  opacity: 0.3,
                }}
              />
              <div
                className="h-2 w-2 rounded-full bg-[#14B8A6]"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0.2s",
                  opacity: 0.3,
                }}
              />
              <div
                className="h-2 w-2 rounded-full bg-[#14B8A6]"
                style={{
                  animation: "pulse 1.4s infinite",
                  animationDelay: "0.4s",
                  opacity: 0.3,
                }}
              />
            </div>
            <p className="text-sm text-[#64748B]">
              Searching medical knowledge base...
            </p>
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

export default AdvancedLoadingIndicator;
