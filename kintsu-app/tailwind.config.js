/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'kintsu-gold': '#D4AF37', // Placeholder gold
        'kintsu-blue': '#0F172A', // Deep Trust Blue (Slate 900)
        'kintsu-grey': '#F1F5F9', // Ash Grey (Slate 100)
      }
    },
  },
  plugins: [],
}