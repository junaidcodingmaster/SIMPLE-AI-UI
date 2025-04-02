const darkThemeToggle = () => {
  const themeToggle = document.getElementById("theme-toggle");

  // Toggle the dark theme class on the body
  document.body.classList.toggle("dark-theme");

  // Check if dark theme is active
  const isDark = document.body.classList.contains("dark-theme");

  // Update the button's aria-label and text content
  themeToggle.setAttribute(
    "aria-label",
    isDark ? "Toggle light mode" : "Toggle dark mode"
  );

  themeToggle.textContent = isDark ? "☀️" : "🌙";
};

darkThemeToggle();
