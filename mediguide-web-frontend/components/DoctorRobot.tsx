"use client";

import { useEffect, useState } from "react";

export type RobotState =
  | "idle"
  | "listening"
  | "thinking"
  | "happy"
  | "error";

export default function DoctorRobot({
  state = "idle",
}: {
  state?: RobotState;
}) {
  const [showWelcome, setShowWelcome] =
    useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setShowWelcome(false);
    }, 5000);

    return () =>
      window.clearTimeout(timer);
  }, []);

  /*
   * Keep the robot visually subtle
   * so it does not cover the chat UI.
   */
  const stateLabel = {
    idle: "",
    listening: "I'm listening 👀",
    thinking: "Let me check that 🤔",
    happy: "I've got an answer! 😊",
    error: "Something went wrong 😟",
  }[state];

  return (
    <div
      className="
        pointer-events-none
        fixed
        bottom-20
        right-3
        z-[60]
        sm:bottom-6
        sm:right-6
      "
      aria-hidden="true"
    >

      {/* =========================================
          SPEECH BUBBLE
      ========================================= */}

      {(showWelcome || state !== "idle") && (
        <div
          className="
            absolute
            bottom-[135px]
            right-0
            w-[205px]
            animate-robot-bubble
            rounded-2xl
            border
            border-primary/15
            bg-white
            px-4
            py-3
            shadow-[0_12px_35px_rgba(15,23,42,0.14)]
            dark:border-white/10
            dark:bg-navy-surface
          "
        >

          <div
            className="
              text-[12px]
              font-semibold
              leading-5
              text-ink
              dark:text-white
            "
          >
            {state === "idle"
              ? "Hi! I'm your MediRAG assistant 👋"
              : stateLabel}
          </div>

          {state === "idle" && (
            <div
              className="
                mt-1
                text-[10px]
                leading-4
                text-ink-soft
                dark:text-slate-400
              "
            >
              Ask me about diseases,
              symptoms and medical information.
            </div>
          )}

          <div
            className="
              absolute
              -bottom-2
              right-8
              h-4
              w-4
              rotate-45
              border-b
              border-r
              border-primary/15
              bg-white
              dark:border-white/10
              dark:bg-navy-surface
            "
          />
        </div>
      )}

      {/* =========================================
          ROBOT
      ========================================= */}

      <div
        className={`
          relative
          h-[125px]
          w-[105px]
          sm:h-[155px]
          sm:w-[130px]

          ${
            state === "thinking"
              ? "animate-robot-thinking"
              : state === "happy"
              ? "animate-robot-happy"
              : state === "listening"
              ? "animate-robot-listening"
              : "animate-robot-idle"
          }
        `}
      >

        {/* Ground shadow */}

        <div
          className="
            absolute
            bottom-0
            left-1/2
            h-5
            w-16
            -translate-x-1/2
            rounded-full
            bg-primary/20
            blur-md
            animate-robot-shadow
          "
        />

        <svg
          viewBox="0 0 180 220"
          className="
            relative
            h-full
            w-full
            overflow-visible
            drop-shadow-[0_14px_22px_rgba(15,23,42,0.20)]
          "
        >

          {/* =======================================
              ANTENNA
          ======================================= */}

          <path
            d="M90 35 C90 25 90 19 90 12"
            stroke="#16A34A"
            strokeWidth="5"
            strokeLinecap="round"
            fill="none"
          />

          <circle
            cx="90"
            cy="10"
            r="7"
            fill={
              state === "thinking"
                ? "#EAB308"
                : state === "error"
                ? "#E11D48"
                : "#16A34A"
            }
            className="animate-robot-blink"
          />

          {/* =======================================
              EARS
          ======================================= */}

          <circle
            cx="27"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          <circle
            cx="153"
            cy="80"
            r="14"
            fill="#16A34A"
          />

          {/* =======================================
              HEAD
          ======================================= */}

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

          <rect
            x="39"
            y="45"
            width="102"
            height="70"
            rx="25"
            fill="#EFF6FF"
          />

          {/* =======================================
              FACE SCREEN
          ======================================= */}

          <rect
            x="45"
            y="51"
            width="90"
            height="58"
            rx="23"
            fill="#0F172A"
          />

          {/* =======================================
              EYES
          ======================================= */}

          <circle
            cx="68"
            cy="76"
            r="6"
            fill="white"
            className="animate-robot-eye"
          />

          <circle
            cx="112"
            cy="76"
            r="6"
            fill="white"
            className="animate-robot-eye"
          />

          {/* =======================================
              MOUTH
          ======================================= */}

          {state === "happy" ? (
            <path
              d="M70 88 Q90 108 110 88"
              stroke="#EAB308"
              strokeWidth="5"
              fill="none"
              strokeLinecap="round"
            />
          ) : state === "thinking" ? (
            <circle
              cx="90"
              cy="94"
              r="5"
              fill="#EAB308"
              className="animate-robot-thinking-dot"
            />
          ) : state === "error" ? (
            <path
              d="M75 100 Q90 88 105 100"
              stroke="#E11D48"
              strokeWidth="5"
              fill="none"
              strokeLinecap="round"
            />
          ) : (
            <path
              d="M75 92 Q90 104 105 92"
              stroke="#EAB308"
              strokeWidth="5"
              fill="none"
              strokeLinecap="round"
            />
          )}

          {/* =======================================
              CHEEKS
          ======================================= */}

          <circle
            cx="55"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity="0.65"
          />

          <circle
            cx="125"
            cy="94"
            r="4"
            fill="#F472B6"
            opacity="0.65"
          />

          {/* =======================================
              NECK
          ======================================= */}

          <rect
            x="76"
            y="123"
            width="28"
            height="12"
            rx="6"
            fill="#16A34A"
          />

          {/* =======================================
              BODY
          ======================================= */}

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

          {/* =======================================
              CHEST PANEL
          ======================================= */}

          <rect
            x="63"
            y="147"
            width="54"
            height="35"
            rx="12"
            fill="#EFF6FF"
          />

          {/* =======================================
              MEDICAL CROSS
          ======================================= */}

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

          {/* =======================================
              LEFT ARM
          ======================================= */}

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

          {/* =======================================
              RIGHT ARM
          ======================================= */}

          <g
            className={
              state === "happy"
                ? "animate-robot-wave"
                : state === "listening"
                ? "animate-robot-listen-arm"
                : ""
            }
            style={{
              transformOrigin:
                "147px 145px",
            }}
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

            <circle
              cx="147"
              cy="190"
              r="11"
              fill="white"
              stroke="#16A34A"
              strokeWidth="4"
            />
          </g>

          {/* =======================================
              STATUS LIGHT
          ======================================= */}

          <circle
            cx="128"
            cy="149"
            r="4"
            fill={
              state === "thinking"
                ? "#EAB308"
                : state === "error"
                ? "#E11D48"
                : "#16A34A"
            }
            className="animate-robot-blink"
          />

        </svg>
      </div>
    </div>
  );
}