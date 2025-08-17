import { ref } from "vue";

const alerts = ref([]);
let nextId = 1;

export function useAlert() {
  const showAlert = (options) => {
    const id = nextId++;
    const alert = {
      id,
      type: options.type || "info",
      title: options.title || "",
      message: options.message || "",
      duration: options.duration || 5000,
      persistent: options.persistent || false,
    };

    alerts.value.push(alert);

    return id;
  };

  const showSuccess = (title, message, duration = 5000) => {
    return showAlert({ type: "success", title, message, duration });
  };

  const showError = (title, message, duration = 7000) => {
    return showAlert({ type: "error", title, message, duration });
  };

  const showWarning = (title, message, duration = 6000) => {
    return showAlert({ type: "warning", title, message, duration });
  };

  const showInfo = (title, message, duration = 5000) => {
    return showAlert({ type: "info", title, message, duration });
  };

  const removeAlert = (id) => {
    const index = alerts.value.findIndex((alert) => alert.id === id);
    if (index > -1) {
      alerts.value.splice(index, 1);
    }
  };

  const clearAll = () => {
    alerts.value = [];
  };

  return {
    alerts,
    showAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeAlert,
    clearAll,
  };
}
