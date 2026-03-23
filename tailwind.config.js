/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  darkMode: "class",
  theme: {
      extend: {
          colors: {
              "primary": "#0f4c81", // Navy Blue
              "navy-light": "#1a62a0",
              "accent-gold": "#C5A028",  // Gold
              "accent-maroon": "#8B3A3A",
              "bone-white": "#F1F4E4", // Bone White
              "background-light": "#F1F4E4",
              "background-dark": "#0a1f33",
              "status-success": "#22c55e",
              "status-success-bg": "#f0fdf4",
              "status-warning": "#f59e0b",
              "status-warning-bg": "#fffbeb",
              "status-danger": "#ef4444",
              "status-danger-bg": "#fef2f2",
              "status-info": "#3b82f6",
              "status-info-bg": "#eff6ff",
          },
          fontFamily: {
              "display": ["Inter", "sans-serif"],
              "clash": ["Clash Display", "sans-serif"],
              "serif": ["Playfair Display", "Georgia", "serif"],
          },
          borderRadius: {
              "DEFAULT": "1rem", "lg": "2rem", "xl": "3rem", "full": "9999px"
          },
      },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
