import type { Config } from "tailwindcss"
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        panel: "var(--panel)",
        "panel-raised": "var(--panel-raised)",
        inset: "var(--inset)",
        brass: "var(--brass)",
        "brass-bright": "var(--brass-bright)",
        paper: "var(--paper)",
        cream: "var(--text)",
        sage: "var(--sage)",
        pink: "var(--pink)",
        line: "var(--line)",
      },
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "16px",
        aegis: "8px",
        "aegis-lg": "16px"
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
        display: ["var(--font-display)"],
      }
    }
  },
  plugins: []
}
export default config
