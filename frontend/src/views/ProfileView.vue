<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Profile Settings</h1>
      <p class="text-gray-600 text-lg">
        Manage your account information and preferences
      </p>
    </div>

    <!-- Main Content -->
    <div v-if="userStore.isAuthenticated" class="space-y-6">
      <!-- Profile Information Card -->
      <Card>
        <CardHeader>
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                ></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">
                Profile Information
              </h3>
              <p class="text-sm text-gray-500">Update your personal details</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="updateProfile" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label for="firstName">First Name</Label>
                <Input
                  id="firstName"
                  v-model="profileForm.firstName"
                  type="text"
                  placeholder="Enter your first name"
                  required
                />
              </div>
              <div>
                <Label for="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  v-model="profileForm.lastName"
                  type="text"
                  placeholder="Enter your last name"
                  required
                />
              </div>
            </div>
            <div>
              <Label for="email">Email Address</Label>
              <Input
                id="email"
                v-model="profileForm.email"
                type="email"
                placeholder="Enter your email address"
                required
              />
              <p class="text-xs text-gray-500 mt-1">Email can be updated</p>
            </div>
            <div>
              <Label for="username">Username</Label>
              <Input
                id="username"
                v-model="profileForm.username"
                type="text"
                placeholder="Choose a username"
                required
              />
            </div>
            <div>
              <Label for="role">Role</Label>
              <Select id="role" v-model="profileForm.role" required>
                <option value="">Select your role</option>
                <option value="auditor">Auditor</option>
                <option value="admin">Admin</option>
              </Select>
            </div>
            <div class="flex justify-end">
              <Button
                type="submit"
                :disabled="profileForm.isLoading"
                class="flex items-center space-x-2"
              >
                <svg
                  v-if="profileForm.isLoading"
                  class="w-4 h-4 animate-spin"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  ></path>
                </svg>
                <span>{{
                  profileForm.isLoading ? "Updating..." : "Update Profile"
                }}</span>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- Change Password Card -->
      <Card>
        <CardHeader>
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                ></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">
                Change Password
              </h3>
              <p class="text-sm text-gray-500">Update your account password</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <Label for="currentPassword">Current Password</Label>
              <Input
                id="currentPassword"
                v-model="passwordForm.currentPassword"
                type="password"
                placeholder="Enter your current password"
                required
              />
            </div>
            <div>
              <Label for="newPassword">New Password</Label>
              <Input
                id="newPassword"
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="Create a new password"
                required
              />
            </div>
            <div>
              <Label for="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="Confirm your new password"
                required
              />
            </div>
            <div class="flex justify-end">
              <Button
                type="submit"
                :disabled="passwordForm.isLoading"
                class="flex items-center space-x-2"
              >
                <svg
                  v-if="passwordForm.isLoading"
                  class="w-4 h-4 animate-spin"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  ></path>
                </svg>
                <span>{{
                  passwordForm.isLoading ? "Changing..." : "Change Password"
                }}</span>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- User Stats Card -->
      <Card>
        <CardHeader>
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-indigo-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                ></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">
                Account Statistics
              </h3>
              <p class="text-sm text-gray-500">Your activity overview</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">
                {{ userStats.totalAudits }}
              </div>
              <div class="text-sm text-gray-500">Total Audits</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">
                {{ userStats.completedAudits }}
              </div>
              <div class="text-sm text-gray-500">Completed</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-yellow-600">
                {{ userStats.pendingAudits }}
              </div>
              <div class="text-sm text-gray-500">Pending</div>
            </div>
          </div>

          <!-- Debug Section -->
          <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="text-sm font-semibold text-gray-700 mb-2">
              Debug Information
            </h4>
            <div class="text-xs text-gray-600 space-y-1">
              <div>
                User Store:
                {{
                  userStore.isAuthenticated
                    ? "Authenticated"
                    : "Not Authenticated"
                }}
              </div>
              <div>
                User Data: {{ userStore.user ? "Available" : "Not Available" }}
              </div>
              <div>Audit Count: {{ auditStore.audits?.length || 0 }}</div>
              <div>Profile Form: {{ JSON.stringify(profileForm) }}</div>
            </div>
            <div class="mt-3 space-x-2">
              <Button @click="testProfileUpdate" size="sm" variant="outline">
                Test Profile Update
              </Button>
              <Button @click="testPasswordChange" size="sm" variant="outline">
                Test Password Change
              </Button>
              <Button @click="refreshUserData" size="sm" variant="outline">
                Refresh User Data
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Welcome Message for Unauthenticated Users -->
    <div v-else class="text-center py-12">
      <div class="max-w-md mx-auto">
        <div
          class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <svg
            class="w-8 h-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Welcome to Profile
        </h3>
        <p class="text-sm text-gray-500 mb-4">
          Please sign in to view and manage your profile
        </p>
        <Button as-child>
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useUserStore } from "../stores/user";
import { useAuditStore } from "../stores/audit";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import { useAlert } from "@/composables/useAlert";

const userStore = useUserStore();
const auditStore = useAuditStore();
const { showAlert } = useAlert();

// Profile form state
const profileForm = reactive({
  firstName: "",
  lastName: "",
  email: "",
  username: "",
  role: "",
  isLoading: false,
});

// Password form state
const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
  isLoading: false,
});

// User stats
const userStats = reactive({
  totalAudits: 0,
  completedAudits: 0,
  pendingAudits: 0,
});

// Initialize profile data
const initializeProfile = () => {
  console.log("🔧 Starting profile initialization...");
  console.log("👤 User store state:", {
    user: userStore.user,
    isAuthenticated: userStore.isAuthenticated,
    isInitialized: userStore.isInitialized,
  });

  if (userStore.user) {
    console.log("🔧 Initializing profile with user data:", userStore.user);

    // Map backend fields to frontend form
    profileForm.firstName = userStore.user.first_name || "";
    profileForm.lastName = userStore.user.last_name || "";
    profileForm.email = userStore.user.email || "";
    profileForm.username = userStore.user.username || "";
    profileForm.role = userStore.user.role || "";

    console.log("📝 Profile form initialized:", profileForm);
  } else {
    console.log("⚠️ No user data available in userStore");
    // Try to get from localStorage directly as fallback
    try {
      const savedUser = localStorage.getItem("user");
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        console.log("📦 Found user data in localStorage:", userData);

        profileForm.firstName = userData.first_name || "";
        profileForm.lastName = userData.last_name || "";
        profileForm.email = userData.email || "";
        profileForm.username = userData.username || "";
        profileForm.role = userData.role || "";

        console.log(
          "📝 Profile form initialized from localStorage:",
          profileForm,
        );
      } else {
        console.log("❌ No user data found in localStorage");
      }
    } catch (error) {
      console.error("❌ Error parsing localStorage user data:", error);
    }
  }
};

// Update profile
const updateProfile = async () => {
  console.log("🚀 Starting profile update...");
  console.log("📝 Current form data:", profileForm);

  // Validation
  if (!profileForm.firstName.trim()) {
    showAlert("First name is required", "error");
    return;
  }

  if (!profileForm.lastName.trim()) {
    showAlert("Last name is required", "error");
    return;
  }

  if (!profileForm.username.trim()) {
    showAlert("Username is required", "error");
    return;
  }

  if (!profileForm.role) {
    showAlert("Please select a role", "error");
    return;
  }

  profileForm.isLoading = true;
  try {
    // Prepare data for backend API
    const profileData = {
      first_name: profileForm.firstName.trim(),
      last_name: profileForm.lastName.trim(),
      email: profileForm.email.trim(),
      username: profileForm.username.trim(),
    };

    console.log("📤 Sending profile update:", profileData);
    console.log("🔐 User store methods available:", {
      hasUpdateProfile: typeof userStore.updateProfile === "function",
      hasGetProfile: typeof userStore.getProfile === "function",
    });

    // Call real API to update profile
    const result = await userStore.updateProfile(profileData);
    console.log("📥 Profile update result:", result);

    if (result.success) {
      showAlert({
        type: "success",
        title: "Profile Updated",
        message: "Your profile has been updated successfully!",
      });

      // Refresh user data
      console.log("🔄 Refreshing user data...");
      const refreshResult = await userStore.getProfile();
      console.log("🔄 User data refresh result:", refreshResult);

      console.log("✅ Profile updated successfully");
    } else {
      throw new Error(result.error || "Unknown error occurred");
    }
  } catch (error) {
    console.error("❌ Profile update failed:", error);
    console.error("❌ Error details:", {
      message: error.message,
      stack: error.stack,
      name: error.name,
    });

    showAlert({
      type: "error",
      title: "Update Failed",
      message: error.message || "Failed to update profile. Please try again.",
    });
  } finally {
    profileForm.isLoading = false;
  }
};

// Change password
const changePassword = async () => {
  console.log("🔐 Starting password change...");
  console.log("🔑 Current password form state:", {
    hasCurrentPassword: !!passwordForm.currentPassword,
    hasNewPassword: !!passwordForm.newPassword,
    hasConfirmPassword: !!passwordForm.confirmPassword,
    passwordsMatch: passwordForm.newPassword === passwordForm.confirmPassword,
  });

  // Validation
  if (!passwordForm.currentPassword.trim()) {
    showAlert("Current password is required", "error");
    return;
  }

  if (!passwordForm.newPassword.trim()) {
    showAlert("New password is required", "error");
    return;
  }

  if (passwordForm.newPassword.length < 8) {
    showAlert("New password must be at least 8 characters long", "error");
    return;
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    showAlert("New passwords do not match", "error");
    return;
  }

  passwordForm.isLoading = true;
  try {
    console.log("🔐 Changing password...");
    console.log("🔐 User store methods available:", {
      hasChangePassword: typeof userStore.changePassword === "function",
    });

    // Call real API to change password
    const result = await userStore.changePassword({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    });

    console.log("📥 Password change result:", result);

    if (result.success) {
      showAlert({
        type: "success",
        title: "Password Changed",
        message: "Your password has been changed successfully!",
      });

      // Reset password form
      passwordForm.currentPassword = "";
      passwordForm.newPassword = "";
      passwordForm.confirmPassword = "";

      console.log("✅ Password changed successfully");
    } else {
      throw new Error(result.error || "Unknown error occurred");
    }
  } catch (error) {
    console.error("❌ Password change failed:", error);
    console.error("❌ Error details:", {
      message: error.message,
      stack: error.stack,
      name: error.name,
    });

    showAlert({
      type: "error",
      title: "Change Failed",
      message: error.message || "Failed to change password. Please try again.",
    });
  } finally {
    passwordForm.isLoading = false;
  }
};

// Calculate user stats
const calculateUserStats = () => {
  console.log("📊 Starting user stats calculation...");
  console.log("📋 Audit store state:", {
    audits: auditStore.audits,
    auditsLength: auditStore.audits?.length || 0,
    hasAudits: !!auditStore.audits,
  });

  const audits = auditStore.audits || [];
  userStats.totalAudits = audits.length;
  userStats.completedAudits = audits.filter(
    (audit) => audit.status === "completed",
  ).length;
  userStats.pendingAudits = audits.filter(
    (audit) => audit.status === "pending",
  ).length;

  console.log("📊 User stats calculated:", userStats);
  console.log("📊 Audit status breakdown:", {
    total: audits.length,
    completed: userStats.completedAudits,
    pending: userStats.pendingAudits,
    other: audits.length - userStats.completedAudits - userStats.pendingAudits,
  });
};

// Watch for user data changes
watch(
  () => userStore.user,
  (newUser) => {
    if (newUser) {
      console.log("👤 User data updated, reinitializing profile:", newUser);
      initializeProfile();
    }
  },
  { immediate: true },
);

// Initialize data when component mounts
onMounted(async () => {
  console.log("🚀 ProfileView mounted, checking auth state...");
  console.log("🔐 Auth state:", {
    isAuthenticated: userStore.isAuthenticated,
    isInitialized: userStore.isInitialized,
    hasUser: !!userStore.user,
    userData: userStore.user,
  });

  if (userStore.isAuthenticated) {
    // Wait a bit for user data to be available
    if (!userStore.user) {
      console.log("⏳ Waiting for user data...");
      await new Promise((resolve) => setTimeout(resolve, 500));

      console.log("⏳ After waiting, user state:", {
        hasUser: !!userStore.user,
        userData: userStore.user,
      });
    }

    console.log("🔧 Initializing profile...");
    initializeProfile();

    // Fetch audits if not already loaded
    if (auditStore.audits.length === 0) {
      console.log("📋 Fetching audits for user stats...");
      try {
        const auditResult = await auditStore.fetchAudits();
        console.log("📋 Audit fetch result:", auditResult);

        if (!auditResult.success) {
          console.warn("⚠️ Audit fetch failed:", auditResult.error);
        }
      } catch (error) {
        console.error("❌ Failed to fetch audits:", error);
        console.error("❌ Error details:", {
          message: error.message,
          stack: error.stack,
          name: error.name,
        });
      }
    } else {
      console.log("📋 Audits already loaded, count:", auditStore.audits.length);
    }

    console.log("📊 Calculating user stats...");
    calculateUserStats();
  } else {
    console.log("❌ User not authenticated, skipping initialization");
  }
});

// Test functions for debugging
const testProfileUpdate = () => {
  console.log("🔄 Testing Profile Update...");
  profileForm.firstName = "TestFirstName";
  profileForm.lastName = "TestLastName";
  profileForm.email = "test@example.com";
  profileForm.username = "testuser";
  profileForm.role = "admin";
  updateProfile();
};

const testPasswordChange = () => {
  console.log("🔐 Testing Password Change...");
  passwordForm.currentPassword = "testPassword";
  passwordForm.newPassword = "newTestPassword123";
  passwordForm.confirmPassword = "newTestPassword123";
  changePassword();
};

const refreshUserData = () => {
  console.log("🔄 Refreshing User Data...");
  userStore.getProfile();
};
</script>

<style scoped>
/* Add any custom styles here */
</style>
