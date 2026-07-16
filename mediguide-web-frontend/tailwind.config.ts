import type { Config } from "tailwindcss";

// Design tokens - "Clinical Field Notes" direction.
// See README.md "Design notes" section for the reasoning behind this
// palette/type system.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F3EE",
        panel: "#ECE7DA",
        ink: "#16262B",
        "ink-soft": "#4B5B5C",
        teal: {
          DEFAULT: "#0E6F63",
          dark: "#0A5750",
          soft: "#E3EEEA",
        },
        amber: {
          DEFAULT: "#C1502E",
          soft: "#F5E4DC",
        },
        verified: {
          DEFAULT: "#2E7D53",
          soft: "#E3EFE4",
        },
        hairline: "#DAD4C4",
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(22, 38, 43, 0.04), 0 4px 16px rgba(22, 38, 43, 0.06)",
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
      },
      animation: {
        pulseline: "pulseline 1.8s linear infinite",
        blink: "blink 1.4s ease-in-out infinite",
        rise: "rise 0.35s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
