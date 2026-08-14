"use client";

const RobotDoctor = () => {
  return (
    <div className="inline-flex items-center justify-center">
      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes pulse-glow {
          0%, 100% {
            box-shadow: 0 0 20px rgba(15, 118, 110, 0.5);
          }
          50% {
            box-shadow: 0 0 40px rgba(20, 184, 166, 0.8);
          }
        }

        @keyframes blink {
          0%, 49%, 100% {
            opacity: 1;
          }
          50%, 99% {
            opacity: 0.3;
          }
        }

        @keyframes rotate-antenna {
          0%, 100% {
            transform: rotate(-5deg);
          }
          50% {
            transform: rotate(5deg);
          }
        }

        .robot-container {
          animation: float 3s ease-in-out infinite;
        }

        .robot-glow {
          animation: pulse-glow 2s ease-in-out infinite;
        }

        .robot-eye {
          animation: blink 3s ease-in-out infinite;
        }

        .robot-antenna {
          animation: rotate-antenna 2s ease-in-out infinite;
          transform-origin: bottom center;
        }
      `}</style>

      <div className="robot-container">
        <div className="robot-glow relative inline-flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-[#0F766E]/20 to-[#14B8A6]/20">
          {/* Head */}
          <div className="relative inline-flex h-16 w-14 flex-col items-center justify-center rounded-lg border-2 border-[#0F766E] bg-gradient-to-br from-[#1A1F35] to-[#0F172A] shadow-lg">
            {/* Antenna */}
            <div className="robot-antenna absolute -top-4 left-1 h-5 w-1 bg-gradient-to-t from-[#14B8A6] to-[#0F766E]" />
            <div className="robot-antenna absolute -top-4 right-1 h-5 w-1 bg-gradient-to-t from-[#14B8A6] to-[#0F766E]" />

            {/* Eyes */}
            <div className="mb-2 flex gap-2">
              <div className="robot-eye h-2 w-2 rounded-full bg-[#14B8A6] shadow-lg" />
              <div className="robot-eye h-2 w-2 rounded-full bg-[#14B8A6] shadow-lg" />
            </div>

            {/* Mouth */}
            <div className="h-1 w-6 rounded-full border-2 border-[#14B8A6]" />

            {/* Body indicator */}
            <div className="mt-2 flex gap-1">
              <div className="h-1 w-1 rounded-full bg-[#0F766E]" />
              <div className="h-1 w-1 rounded-full bg-[#14B8A6]" />
              <div className="h-1 w-1 rounded-full bg-[#0F766E]" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RobotDoctor;
