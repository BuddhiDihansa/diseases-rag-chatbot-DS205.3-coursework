import type { Config } from "tailwindcss";

// "Green Signal" palette: green is the brand/primary action color
// (buttons, verified state, active nav item), light yellow is the
// secondary accent (AI trace tags, subtle highlights). Neutral
// light/dark bases keep body text readable - the two brand hues are
// used deliberately, not painted across every surface.
const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
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
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06)",
      },
      keyframes: {
        pulseline: {
          "0%": { strokeDashoffset: "240" },
          "100%": { strokeDashoffset: "0" },
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.25" },
        },
        rise: {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        drift: {
          "0%": { transform: "translate3d(0,0,0)" },
          "100%": { transform: "translate3d(2%, -3%, 0)" },
        },
      },
      animation: {
        pulseline: "pulseline 1.6s linear infinite",
        "pulseline-idle": "pulseline 6s linear infinite",
        blink: "blink 1.4s ease-in-out infinite",
        rise: "rise 0.35s ease-out both",
        drift: "drift 16s ease-in-out infinite alternate",
      },
    },
  },
  plugins: [],
};

export default config;