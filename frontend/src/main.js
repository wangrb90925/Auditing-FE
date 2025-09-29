import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";
import "./style.css";
import { globalErrorHandler } from "./utils/errorHandler";

const app = createApp(App);
const pinia = createPinia();

// Set up global error handler
app.config.errorHandler = globalErrorHandler;

app.use(pinia);
app.use(router);

app.mount("#app");
