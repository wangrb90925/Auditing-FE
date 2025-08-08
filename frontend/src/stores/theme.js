import { ref, watch } from "vue";

const theme = ref(localStorage.getItem("theme") || "light");

// Apply theme to document
const applyTheme = (newTheme) => {
  const root = document.documentElement;
  if (newTheme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
  localStorage.setItem("theme", newTheme);
};

// Initialize theme on app start
applyTheme(theme.value);

// Watch for theme changes
watch(theme, (newTheme) => {
  applyTheme(newTheme);
});

export const useThemeStore = () => {
  const toggleTheme = () => {
    theme.value = theme.value === "light" ? "dark" : "light";
  };

  const setTheme = (newTheme) => {
    theme.value = newTheme;
  };

  return {
    theme,
    toggleTheme,
    setTheme,
  };
};
