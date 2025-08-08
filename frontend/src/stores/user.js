import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useUserStore = defineStore("user", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("auth_token") || null);

  const isAuthenticated = computed(() => !!token.value);

  const login = async (credentials) => {
    try {
      // Simulate API call - replace with actual authentication
      if (
        credentials.username === "admin" &&
        credentials.password === "password"
      ) {
        const mockUser = {
          id: 1,
          name: "Admin User",
          email: "admin@cdlmanager.com",
          role: "admin",
        };
        const mockToken = "mock-jwt-token-" + Date.now();

        user.value = mockUser;
        token.value = mockToken;
        localStorage.setItem("auth_token", mockToken);
        localStorage.setItem("user", JSON.stringify(mockUser));

        return { success: true };
      } else {
        throw new Error("Invalid credentials");
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const signup = async (userData) => {
    try {
      // Simulate API call - replace with actual signup
      // In a real app, this would create a new user account
      const mockUser = {
        id: Date.now(),
        name: userData.fullName,
        email: userData.email,
        role: userData.role,
      };
      const mockToken = "mock-jwt-token-" + Date.now();

      user.value = mockUser;
      token.value = mockToken;
      localStorage.setItem("auth_token", mockToken);
      localStorage.setItem("user", JSON.stringify(mockUser));

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    user.value = null;
    token.value = null;
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
  };

  const initializeAuth = () => {
    const savedToken = localStorage.getItem("auth_token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
      token.value = savedToken;
      user.value = JSON.parse(savedUser);
    }
  };

  // Initialize auth on store creation
  initializeAuth();

  return {
    user,
    token,
    isAuthenticated,
    login,
    signup,
    logout,
    initializeAuth,
  };
});
