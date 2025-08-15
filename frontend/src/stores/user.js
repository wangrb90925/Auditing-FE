import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { apiService } from "../lib/api";

export const useUserStore = defineStore("user", () => {
  const user = ref(null);
  const accessToken = ref(localStorage.getItem("access_token") || null);
  const refreshToken = ref(localStorage.getItem("refresh_token") || null);

  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => user.value?.role === "admin");
  const isAuditor = computed(
    () => user.value?.role === "auditor" || user.value?.role === "admin"
  );

  // Store tokens and user data
  const storeAuthData = (authData) => {
    accessToken.value = authData.access_token;
    refreshToken.value = authData.refresh_token;
    user.value = authData.user;

    localStorage.setItem("access_token", authData.access_token);
    localStorage.setItem("refresh_token", authData.refresh_token);
    localStorage.setItem("user", JSON.stringify(authData.user));
  };

  // Clear auth data
  const clearAuthData = () => {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  };

  const login = async (credentials) => {
    try {
      const response = await apiService.login(credentials);
      storeAuthData(response);
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return { success: false, error: error.message };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await apiService.register(userData);
      storeAuthData(response);
      return { success: true };
    } catch (error) {
      console.error("Signup failed:", error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    clearAuthData();
  };

  const refreshAuth = async () => {
    try {
      const response = await apiService.refreshToken();
      storeAuthData(response);
      return { success: true };
    } catch (error) {
      console.error("Token refresh failed:", error);
      clearAuthData();
      return { success: false, error: error.message };
    }
  };

  const getProfile = async () => {
    try {
      const profile = await apiService.getProfile();
      user.value = profile;
      localStorage.setItem("user", JSON.stringify(profile));
      return { success: true, profile };
    } catch (error) {
      console.error("Get profile failed:", error);
      return { success: false, error: error.message };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await apiService.updateProfile(profileData);
      user.value = response.user;
      localStorage.setItem("user", JSON.stringify(response.user));
      return { success: true, user: response.user };
    } catch (error) {
      console.error("Update profile failed:", error);
      return { success: false, error: error.message };
    }
  };

  const initializeAuth = async () => {
    const savedAccessToken = localStorage.getItem("access_token");
    const savedRefreshToken = localStorage.getItem("refresh_token");
    const savedUser = localStorage.getItem("user");

    if (savedAccessToken && savedUser) {
      accessToken.value = savedAccessToken;
      refreshToken.value = savedRefreshToken;
      user.value = JSON.parse(savedUser);

      // Try to refresh token if it's close to expiring
      try {
        await refreshAuth();
      } catch (error) {
        console.warn("Token refresh failed during initialization:", error);
        // Don't clear auth data here, let the user continue with current token
      }
    }
  };

  // Initialize auth on store creation
  initializeAuth();

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAdmin,
    isAuditor,
    login,
    signup,
    logout,
    refreshAuth,
    getProfile,
    updateProfile,
    initializeAuth,
  };
});
