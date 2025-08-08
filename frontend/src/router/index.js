import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "../stores/user";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginView.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/signup",
    name: "Signup",
    component: () => import("../views/SignupView.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("../views/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/upload",
    name: "Upload",
    component: () => import("../views/UploadView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/audits",
    name: "Audits",
    component: () => import("../views/AuditsView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/audit/:id",
    name: "AuditDetail",
    component: () => import("../views/AuditDetailView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next("/login");
  } else if (
    (to.path === "/login" || to.path === "/signup") &&
    userStore.isAuthenticated
  ) {
    next("/dashboard");
  } else {
    next();
  }
});

export default router;
