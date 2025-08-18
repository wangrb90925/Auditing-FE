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
            <div>
              <Label for="fullName">Full Name</Label>
              <Input
                id="fullName"
                v-model="profileForm.fullName"
                type="text"
                placeholder="Enter your full name"
                required
              />
            </div>
            <div>
              <Label for="email">Email Address</Label>
              <Input
                id="email"
                v-model="profileForm.email"
                type="email"
                placeholder="Enter your email address"
                required
                disabled
              />
              <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
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
              <Label for="password">Password</Label>
              <Input
                id="password"
                v-model="passwordForm.password"
                type="password"
                placeholder="Create a password"
                required
              />
            </div>
            <div>
              <Label for="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="Confirm your password"
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
  fullName: "",
  email: "",
  username: "",
  role: "",
  isLoading: false,
});

// Password form state
const passwordForm = reactive({
  password: "",
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
  if (userStore.user) {
    // Handle the actual user data structure from backend
    const firstName = userStore.user.first_name || "";
    const lastName = userStore.user.last_name || "";
    profileForm.fullName = `${firstName} ${lastName}`.trim() || "";
    profileForm.email = userStore.user.email || "";
    profileForm.username = userStore.user.username || "";
    profileForm.role = userStore.user.role || "";

    console.log("🔧 Initializing profile with user data:", userStore.user);
    console.log("📝 Profile form initialized:", profileForm);
  } else {
    console.log("⚠️ No user data available in userStore");
    // Try to get from localStorage directly as fallback
    try {
      const savedUser = localStorage.getItem("user");
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        console.log("📦 Found user data in localStorage:", userData);

        const firstName = userData.first_name || "";
        const lastName = userData.last_name || "";
        profileForm.fullName = `${firstName} ${lastName}`.trim() || "";
        profileForm.email = userData.email || "";
        profileForm.username = userData.username || "";
        profileForm.role = userData.role || "";

        console.log(
          "📝 Profile form initialized from localStorage:",
          profileForm
        );
      }
    } catch (error) {
      console.error("❌ Error parsing localStorage user data:", error);
    }
  }
};

// Update profile
const updateProfile = async () => {
  // Validation
  if (!profileForm.fullName.trim()) {
    showAlert("Full name is required", "error");
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
    // Here you would typically call an API to update the profile
    // For now, we'll just simulate the update
    await new Promise((resolve) => setTimeout(resolve, 1000));

    showAlert({
      type: "success",
      title: "Profile Updated",
      message: "Your profile has been updated successfully!",
    });

    // Update the user store if needed
    if (userStore.user) {
      userStore.user.fullName = profileForm.fullName;
      userStore.user.username = profileForm.username;
      userStore.user.role = profileForm.role;
    }
  } catch (error) {
    showAlert({
      type: "error",
      title: "Update Failed",
      message: "Failed to update profile. Please try again.",
    });
  } finally {
    profileForm.isLoading = false;
  }
};

// Change password
const changePassword = async () => {
  // Validation
  if (!passwordForm.password.trim()) {
    showAlert("Password is required", "error");
    return;
  }

  if (passwordForm.password.length < 8) {
    showAlert("Password must be at least 8 characters long", "error");
    return;
  }

  if (passwordForm.password !== passwordForm.confirmPassword) {
    showAlert("Passwords do not match", "error");
    return;
  }

  passwordForm.isLoading = true;
  try {
    // Here you would typically call an API to change the password
    // For now, we'll just simulate the change
    await new Promise((resolve) => setTimeout(resolve, 1000));

    showAlert({
      type: "success",
      title: "Password Changed",
      message: "Your password has been changed successfully!",
    });

    // Reset password form
    passwordForm.password = "";
    passwordForm.confirmPassword = "";
  } catch (error) {
    showAlert({
      type: "error",
      title: "Change Failed",
      message: "Failed to change password. Please try again.",
    });
  } finally {
    passwordForm.isLoading = false;
  }
};

// Calculate user stats
const calculateUserStats = () => {
  const audits = auditStore.audits || [];
  userStats.totalAudits = audits.length;
  userStats.completedAudits = audits.filter(
    (audit) => audit.status === "completed"
  ).length;
  userStats.pendingAudits = audits.filter(
    (audit) => audit.status === "pending"
  ).length;
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
  { immediate: true }
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
    }

    initializeProfile();

    if (auditStore.audits.length === 0) {
      await auditStore.fetchAudits();
    }
    calculateUserStats();
  }
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
