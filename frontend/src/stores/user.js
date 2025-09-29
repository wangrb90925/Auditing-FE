import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { apiService } from "../lib/api";

export const useUserStore = defineStore("user", () => {
  const user = ref(null);
  const accessToken = ref(localStorage.getItem("access_token") || null);
  const isInitialized = ref(false);

  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => user.value?.role === "admin");
  const isAuditor = computed(
    () => user.value?.role === "auditor" || user.value?.role === "admin"
  );

  // Role-based permissions
  const canUpload = computed(() => {
    return isAuditor.value || isAdmin.value;
  });

  const canReview = computed(() => {
    return isAuditor.value || isAdmin.value;
  });

  const canDownload = computed(() => {
    return isAuditor.value || isAdmin.value;
  });

  const canManageUsers = computed(() => {
    return isAdmin.value;
  });

  const canViewLogs = computed(() => {
    return isAdmin.value;
  });

  // Store tokens and user data
  const storeAuthData = (authData) => {
    accessToken.value = authData.access_token;
    user.value = authData.user;

    localStorage.setItem("access_token", authData.access_token);
    localStorage.setItem("user", JSON.stringify(authData.user));
  };

  // Clear auth data
  const clearAuthData = () => {
    accessToken.value = null;
    user.value = null;

    localStorage.removeItem("access_token");
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

  const changePassword = async (passwordData) => {
    try {
      const response = await apiService.changePassword(passwordData);
      return { success: true, message: response.message };
    } catch (error) {
      console.error("Change password failed:", error);
      return { success: false, error: error.message };
    }
  };

  const initializeAuth = async () => {
    console.log("🔧 Starting auth initialization...");
    try {
      const savedAccessToken = localStorage.getItem("access_token");
      const savedUser = localStorage.getItem("user");

      console.log("📦 Found saved data:", {
        hasToken: !!savedAccessToken,
        hasUser: !!savedUser,
      });

      if (savedAccessToken && savedUser) {
        accessToken.value = savedAccessToken;
        user.value = JSON.parse(savedUser);
        console.log("✅ Restored auth data from localStorage");
      } else {
        console.log("ℹ️ No saved auth data found");
      }
    } catch (error) {
      console.error("❌ Error during auth initialization:", error);
      // Clear invalid data
      clearAuthData();
    } finally {
      // Always set initialized to true to prevent infinite loading
      console.log("🏁 Setting isInitialized to true");
      isInitialized.value = true;
    }
  };

  // Initialize auth on store creation with a timeout fallback
  initializeAuth();

  // Safety timeout to ensure initialization completes
  setTimeout(() => {
    if (!isInitialized.value) {
      console.warn("Auth initialization timeout, forcing completion");
      isInitialized.value = true;
    }
  }, 2000); // 2 second timeout

  return {
    user,
    accessToken,
    isInitialized,
    isAuthenticated,
    isAdmin,
    isAuditor,
    canUpload,
    canReview,
    canDownload,
    canManageUsers,
    canViewLogs,
    login,
    signup,
    logout,
    getProfile,
    updateProfile,
    changePassword,
    initializeAuth,
  };
});
