/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#241910",
        "ink-soft": "#5e534a",
        paper: "#f3eee6",
        cream: "#faf7f2",
        espresso: "#1a120e",
        blush: "#c9847a",
        gold: "#a6845a",
        moss: "#2f6a56",
        line: "#e3d8cb",
        mist: "#efe7dc",
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        sans: ["Outfit", "ui-sans-serif", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 0 rgba(36, 25, 16, 0.04), 0 16px 40px rgba(36, 25, 16, 0.05)",
      },
    },
  },
  plugins: [],
};
