"use client";

import { useEffect, useState } from "react";

export type RobotState =
  | "welcome"
  | "idle"
  | "listening"
  | "thinking"
  | "happy";

interface DoctorRobotProps {
  state?: RobotState;
}

export default function DoctorRobot({
  state = "idle",
}: DoctorRobotProps) {
  const [showBubble, setShowBubble] = useState(state === "welcome");

  useEffect(() => {
    if (state === "welcome") {
      setShowBubble(true);

      const timer = window.setTimeout(() => {
        setShowBubble(false);
      }, 4200);

      return () => window.clearTimeout(timer);
    }

    setShowBubble(false);
  }, [state]);

  const face =
    state === "thinking"
      ? "thinking"
      : state === "happy"
        ? "happy"
        : state === "listening"
          ? "listening"
          : "normal";

  return (
    <div
      className="pointer-events-none fixed bottom-20 right-3 z-[60] sm:bottom-6 sm:right-6"
      aria-hidden="true"
    >
      {/* Speech bubble */}
      {showBubble && (
        <div className="absolute bottom-[118px] right-0 w-[190px] animate-robot-bubble rounded-2xl border border-primary/15 bg-white px-4 py-3 shadow-[0_12px_35px_rgba(15,23,42,0.12)] dark:border-white/10 dark:bg-navy-surface">
          <div className="text-[12px] font-semibold leading-5 text-ink dark:text-white">
            Hi! I&apos;m your MediRAG assistant 👋
          </div>

          <div className="absolute -bottom-2 right-7 h-4 w-4 rotate-45 border-b border-r border-primary/15 bg-white dark:border-white/10 dark:bg-navy-surface" />
        </div>
      )}

      {/* Robot */}
      <div
        className={`
          relative
          h-[112px] w-[92px]
          sm:h-[145px] sm:w-[120px]
          ${
            state === "thinking"
              ? "animate-robot-thinking"
              : state === "happy"
                ? "animate-robot-happy"
                : state === "welcome"
                  ? "animate-robot-welcome"
                  : "animate-robot-idle"
          }
        `}
      >
        {/* Glow */}
        <div
          className={`
            absolute
            bottom-0
            left-1/2
            h-5
            w-16
            -translate-x-1/2
            rounded-full
            bg-primary/15
            blur-md
            transition-all
            duration-500
            ${
              state === "thinking"
                ? "scale-75 opacity-40"
                : state === "happy"
                  ? "scale-125 opacity-80"
                  : "scale-100 opacity-60"
            }
          `}
        />

        <svg
          viewBox="0 0 180 220"
          className="relative h-full w-full overflow-visible drop-shadow-[0_16px_24px_rgba(15,23,42,0.18)]"
        >
          {/* Antenna */}
          <g className="origin-bottom">
            <path
              d="M90 35 C90 25 90 20 90 12"
              stroke="#16A34A"
              strokeWidth="5"
              strokeLinecap="round"
              fill="none"
            />

            <circle
              cx="90"
              cy="10"
              r="7"
              fill="#EAB308"
              className="animate-robot-sensor"
            />
          </g>

          {/* Left ear */}
          <circle
            cx="27"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          {/* Right ear */}
          <circle
            cx="153"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          {/* Head */}
          <rect
            x="28"
            y="34"
            width="124"
            height="92"
            rx="34"
            fill="white"
            stroke="#16A34A"
            strokeWidth="5"
          />

          {/* Blue inner head glow */}
          <rect
            x="39"
            y="45"
            width="102"
            height="70"
            rx="25"
            fill="#EFF6FF"
            opacity="0.7"
          />

          {/* Face screen */}
          <rect
            x="45"
            y="51"
            width="90"
            height="58"
            rx="23"
            fill="#0F172A"
          />

          {/* Normal eyes */}
          {face === "normal" && (
            <>
              <path
                d="M62 76 Q69 65 76 76"
                stroke="#FFFFFF"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
                className="animate-robot-blink"
              />

              <path
                d="M104 76 Q111 65 118 76"
                stroke="#FFFFFF"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
                className="animate-robot-blink"
              />

              <path
                d="M78 91 Q90 101 102 91"
                stroke="#EAB308"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
              />
            </>
          )}

          {/* Listening eyes */}
          {face === "listening" && (
            <>
              <circle
                cx="67"
                cy="77"
                r="6"
                fill="#FFFFFF"
              />

              <circle
                cx="113"
                cy="77"
                r="6"
                fill="#FFFFFF"
              />

              <path
                d="M77 94 Q90 101 103 94"
                stroke="#EAB308"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
              />
            </>
          )}

          {/* Thinking face */}
          {face === "thinking" && (
            <>
              <circle
                cx="67"
                cy="77"
                r="5"
                fill="#FFFFFF"
                className="animate-robot-eye"
              />

              <circle
                cx="113"
                cy="77"
                r="5"
                fill="#FFFFFF"
                className="animate-robot-eye"
              />

              <path
                d="M78 96 Q90 90 102 96"
                stroke="#EAB308"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
              />
            </>
          )}

          {/* Happy face */}
          {face === "happy" && (
            <>
              <path
                d="M61 78 Q68 67 75 78"
                stroke="#FFFFFF"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
              />

              <path
                d="M105 78 Q112 67 119 78"
                stroke="#FFFFFF"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
              />

              <path
                d="M74 91 Q90 107 106 91"
                stroke="#EAB308"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
              />
            </>
          )}

          {/* Cheek lights */}
          <circle
            cx="53"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity={state === "happy" ? "0.9" : "0.35"}
          />

          <circle
            cx="127"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity={state === "happy" ? "0.9" : "0.35"}
          />

          {/* Neck */}
          <rect
            x="76"
            y="123"
            width="28"
            height="12"
            rx="6"
            fill="#16A34A"
          />

          {/* Body */}
          <rect
            x="39"
            y="132"
            width="102"
            height="67"
            rx="30"
            fill="white"
            stroke="#16A34A"
            strokeWidth="5"
          />

          {/* Chest panel */}
          <rect
            x="63"
            y="147"
            width="54"
            height="35"
            rx="12"
            fill="#EFF6FF"
          />

          {/* Medical cross */}
          <rect
            x="86"
            y="153"
            width="8"
            height="23"
            rx="2"
            fill="#16A34A"
          />

          <rect
            x="78"
            y="161"
            width="24"
            height="8"
            rx="2"
            fill="#16A34A"
          />

          {/* Left arm */}
          <g className="origin-[48px_145px]">
            <rect
              x="22"
              y="139"
              width="21"
              height="47"
              rx="10"
              fill="white"
              stroke="#16A34A"
              strokeWidth="5"
            />
          </g>

          {/* Right waving arm */}
          <g
            className={
              state === "welcome" || state === "happy"
                ? "animate-robot-wave"
                : ""
            }
            style={{ transformOrigin: "137px 145px" }}
          >
            <rect
              x="137"
              y="139"
              width="21"
              height="47"
              rx="10"
              fill="white"
              stroke="#16A34A"
              strokeWidth="5"
            />

            {/* hand */}
            <circle
              cx="147"
              cy="190"
              r="11"
              fill="white"
              stroke="#16A34A"
              strokeWidth="4"
            />
          </g>

          {/* Small chest light */}
          <circle
            cx="128"
            cy="149"
            r="4"
            fill="#EAB308"
            className="animate-robot-sensor"
          />
        </svg>
      </div>
    </div>
  );
}