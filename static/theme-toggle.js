document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("theme-toggle");

  if (!toggleButton) return;

  const body = document.body;

  // Function to set the theme
  const setTheme = (isDark) => {
    if (isDark) {
      body.classList.add("dark-theme");
      toggleButton.innerHTML = `<img src="/static/svgs/dark-mode.svg" alt="Dark Mode" width="24" height="24">`;
    } else {
      body.classList.remove("dark-theme");
      toggleButton.innerHTML = `<img src="/static/svgs/light-mode.svg" alt="Light Mode" width="24" height="24">`;
    }
    // Save the theme preference to localStorage
    localStorage.setItem("theme", isDark ? "dark" : "light");
  };

  // Function to toggle the theme
  const toggleTheme = () => {
    const isDark = !body.classList.contains("dark-theme");
    setTheme(isDark);
  };

  // Check for saved theme preference
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    setTheme(true);
  } else if (savedTheme === "light") {
    setTheme(false);
  } else {
    // Default to light theme if no preference is saved
    setTheme(false);
  }

  // Add event listener to the toggle button
  toggleButton.addEventListener("click", toggleTheme);
});
