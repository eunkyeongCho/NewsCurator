import "@/assets/scss/main.scss";
import { createApp } from "vue";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import App from "@/App.vue";
import router from "@/router";
import { createPinia } from "pinia";
import axios from "axios";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);

axios.interceptors.request.use(config => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

app.mount("#app");
