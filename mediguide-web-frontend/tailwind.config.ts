import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",

  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        paper: "#FAFDFB",
        panel: "#FFFFFF",
        ink: "#0F172A",
        "ink-soft": "#5B6478",
        hairline: "#E2E8E4",

        sidebar: {
          DEFAULT: "#F3FAF4",
          border: "#DCEEDD",
        },

        navy: {
          DEFAULT: "#0B1120",
          surface: "#131C2E",
          border: "#232E45",
        },

        primary: {
          DEFAULT: "#16A34A",
          dark: "#15803D",
          soft: "#DCFCE7",
        },

        accent: {
          DEFAULT: "#EAB308",
          dark: "#A16207",
          soft: "#FEF9C3",
        },

        amber: {
          DEFAULT: "#D97706",
          soft: "#FEF3C7",
        },

        rose: {
          DEFAULT: "#E11D48",
          soft: "#FFE4E6",
        },
      },

      fontFamily: {
        display: [
          "var(--font-display)",
          "system-ui",
          "sans-serif",
        ],

        body: [
          "var(--font-body)",
          "system-ui",
          "sans-serif",
        ],

        mono: [
          "var(--font-mono)",
          "monospace",
        ],
      },

      boxShadow: {
        card:
          "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06)",
      },

      keyframes: {
        pulseline: {
          "0%": {
            strokeDashoffset: "240",
          },
          "100%": {
            strokeDashoffset: "0",
          },
        },

        blink: {
          "0%, 100%": {
            opacity: "1",
          },
          "50%": {
            opacity: "0.25",
          },
        },

        rise: {
          "0%": {
            opacity: "0",
            transform: "translateY(6px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },

        drift: {
          "0%": {
            transform: "translate3d(0,0,0)",
          },
          "100%": {
            transform: "translate3d(2%, -3%, 0)",
          },
        },

        roam: {
          "0%": {
            left: "30%",
            top: "12%",
          },
          "20%": {
            left: "90%",
            top: "9%",
          },
          "40%": {
            left: "92%",
            top: "55%",
          },
          "60%": {
            left: "60%",
            top: "86%",
          },
          "80%": {
            left: "32%",
            top: "58%",
          },
          "100%": {
            left: "30%",
            top: "12%",
          },
        },

        bob: {
          "0%, 100%": {
            transform:
              "translateY(0) rotate(-2deg)",
          },
          "50%": {
            transform:
              "translateY(-10px) rotate(2deg)",
          },
        },

        wave: {
          "0%, 100%": {
            transform: "rotate(-8deg)",
          },
          "50%": {
            transform: "rotate(24deg)",
          },
        },

        robotIdle: {
          "0%, 100%": {
            transform:
              "translateY(0px) rotate(-1deg)",
          },
          "50%": {
            transform:
              "translateY(-7px) rotate(1deg)",
          },
        },

        robotWelcome: {
          "0%": {
            opacity: "0",
            transform:
              "translate(35px, 25px) scale(0.75)",
          },

          "60%": {
            opacity: "1",
            transform:
              "translate(-5px, -4px) scale(1.04)",
          },

          "100%": {
            opacity: "1",
            transform:
              "translate(0, 0) scale(1)",
          },
        },

        robotWave: {
          "0%, 100%": {
            transform: "rotate(0deg)",
          },

          "30%": {
            transform: "rotate(-20deg)",
          },

          "60%": {
            transform: "rotate(18deg)",
          },
        },

        robotBlink: {
          "0%, 92%, 100%": {
            opacity: "1",
          },

          "95%": {
            opacity: "0.15",
          },
        },

        robotEye: {
          "0%, 100%": {
            transform: "scale(1)",
          },

          "50%": {
            transform: "scale(0.85)",
          },
        },

        robotShadow: {
          "0%, 100%": {
            transform:
              "translateX(-50%) scaleX(1)",
            opacity: "0.55",
          },

          "50%": {
            transform:
              "translateX(-50%) scaleX(0.75)",
            opacity: "0.25",
          },
        },

        robotBubble: {
          "0%": {
            opacity: "0",
            transform:
              "translateY(8px) scale(0.94)",
          },

          "100%": {
            opacity: "1",
            transform:
              "translateY(0) scale(1)",
          },
        },

        /* =====================================
           NEW INTERACTION ANIMATIONS
        ===================================== */

        robotThinking: {
          "0%, 100%": {
            transform:
              "translateY(0) rotate(-1deg)",
          },

          "50%": {
            transform:
              "translateY(-4px) rotate(3deg)",
          },
        },

        robotHappy: {
          "0%, 100%": {
            transform:
              "translateY(0) rotate(-2deg)",
          },

          "25%": {
            transform:
              "translateY(-9px) rotate(3deg)",
          },

          "50%": {
            transform:
              "translateY(-4px) rotate(-2deg)",
          },

          "75%": {
            transform:
              "translateY(-9px) rotate(3deg)",
          },
        },

        robotListening: {
          "0%, 100%": {
            transform:
              "translateY(0) rotate(0deg)",
          },

          "50%": {
            transform:
              "translateY(-5px) rotate(-2deg)",
          },
        },

        robotThinkingDot: {
          "0%, 100%": {
            transform: "scale(0.7)",
            opacity: "0.5",
          },

          "50%": {
            transform: "scale(1.15)",
            opacity: "1",
          },
        },

        robotListenArm: {
          "0%, 100%": {
            transform: "rotate(0deg)",
          },

          "50%": {
            transform: "rotate(-8deg)",
          },
        },
      },

      animation: {
        pulseline:
          "pulseline 1.6s linear infinite",

        "pulseline-idle":
          "pulseline 6s linear infinite",

        blink:
          "blink 1.4s ease-in-out infinite",

        rise:
          "rise 0.35s ease-out both",

        drift:
          "drift 16s ease-in-out infinite alternate",

        roam:
          "roam 38s ease-in-out infinite",

        bob:
          "bob 2.6s ease-in-out infinite",

        wave:
          "wave 1.8s ease-in-out infinite",

        "robot-idle":
          "robotIdle 3.2s ease-in-out infinite",

        "robot-welcome":
          "robotWelcome 0.8s cubic-bezier(.2,.8,.2,1) both",

        "robot-wave":
          "robotWave 0.9s ease-in-out infinite",

        "robot-blink":
          "robotBlink 4s ease-in-out infinite",

        "robot-eye":
          "robotEye 1.8s ease-in-out infinite",

        "robot-shadow":
          "robotShadow 3.2s ease-in-out infinite",

        "robot-bubble":
          "robotBubble 0.35s ease-out both",

        "robot-thinking":
          "robotThinking 2s ease-in-out infinite",

        "robot-happy":
          "robotHappy 1.8s ease-in-out infinite",

        "robot-listening":
          "robotListening 2.4s ease-in-out infinite",

        "robot-thinking-dot":
          "robotThinkingDot 1s ease-in-out infinite",

        "robot-listen-arm":
          "robotListenArm 1.5s ease-in-out infinite",
      },
    },
  },

  plugins: [],
};

export default config;