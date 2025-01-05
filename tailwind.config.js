/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Important: Look for HTML files in the templates folder and its subfolders
    "./static/js/**/*.js", // If you use Tailwind classes in your JavaScript files
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")], // Add daisyUI plugin
  safelist: [
    "alert",
    "alert-success",
    "alert-warning",
    "alert-error",
    "alert-info"
  ],
}

