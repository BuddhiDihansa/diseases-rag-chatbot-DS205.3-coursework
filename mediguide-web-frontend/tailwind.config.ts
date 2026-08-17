import type { Config } from "tailwindcss";

// MediRAG Tailwind configuration
// Green = primary medical/AI brand
// Yellow = secondary AI accent

const config: Config = {
  darkMode: "class",

  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],

  theme: {
    extend: {
      /* =========================================
         COLORS
      ========================================= */

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

      /* =========================================
         FONTS
      ========================================= */

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

      /* =========================================
         SHADOWS
      ========================================= */

      boxShadow: {
        card:
          "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06)",
      },

      /* =========================================
         KEYFRAMES
      ========================================= */

      keyframes: {
        /* -----------------------------------------
           EXISTING WEBSITE ANIMATIONS
        ----------------------------------------- */

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

        /* -----------------------------------------
           OLD ROBOT ANIMATIONS
           Kept so nothing else breaks.
        ----------------------------------------- */

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
            transform: "translateY(0) rotate(-2deg)",
          },

          "50%": {
            transform: "translateY(-10px) rotate(2deg)",
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

        /* =========================================
           NEW MEDIRAG ROBOT ANIMATIONS
        ========================================= */

        /**
         * Main idle movement.
         *
         * The robot gently floats up and down.
         * Slow enough that it does not distract the user.
         */
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

        /**
         * Robot hand wave.
         */
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

        /**
         * Antenna / small light blinking.
         */
        robotBlink: {
          "0%, 92%, 100%": {
            opacity: "1",
          },

          "95%": {
            opacity: "0.15",
          },
        },

        /**
         * Small eye movement.
         */
        robotEye: {
          "0%, 100%": {
            transform: "scale(1)",
          },

          "50%": {
            transform: "scale(0.85)",
          },
        },
      },

      /* =========================================
         ANIMATIONS
      ========================================= */

      animation: {
        /* -----------------------------------------
           EXISTING WEBSITE ANIMATIONS
        ----------------------------------------- */

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

        /* -----------------------------------------
           MEDIRAG ROBOT
        ----------------------------------------- */

        /**
         * Robot floating.
         */
        "robot-idle":
          "robotIdle 3.2s ease-in-out infinite",

        /**
         * Robot waving.
         */
        "robot-wave":
          "robotWave 0.9s ease-in-out infinite",

        /**
         * Robot antenna blinking.
         */
        "robot-blink":
          "robotBlink 4s ease-in-out infinite",

        /**
         * Robot eyes.
         */
        "robot-eye":
          "robotEye 1.8s ease-in-out infinite",
      },
    },
  },

  plugins: [],
};

export default config;