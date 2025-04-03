document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("theme-toggle");

  if (!toggleButton) return;
  const body = document.body;
  toggleButton.addEventListener("click", () => {
    const isDark = body.classList.toggle("dark-theme");
    toggleButton.innerHTML = isDark
      ? `<img src="/static/svgs/dark-mode.svg" alt="Dark Mode" width="24" height="24">`
      : `<img src="/static/svgs/light-mode.svg" alt="Light Mode" width="24" height="24">`;
  });
});
