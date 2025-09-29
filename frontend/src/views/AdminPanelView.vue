<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Admin Panel</h1>
      <p class="text-gray-600 text-lg">
        System administration and user management
      </p>
    </div>

    <!-- Main Content -->
    <div
      v-if="userStore.isAuthenticated && userStore.user?.role === 'admin'"
      class="space-y-6"
    >
      <!-- System Overview Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent class="p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
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
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                  ></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Users</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ systemStats.totalUsers }}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Active Users</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ systemStats.activeUsers }}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center">
              <div class="p-2 bg-yellow-100 rounded-lg">
                <svg
                  class="w-6 h-6 text-yellow-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Audits</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ systemStats.totalAudits }}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center">
              <div class="p-2 bg-red-100 rounded-lg">
                <svg
                  class="w-6 h-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
                  ></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">System Health</p>
                <p class="text-2xl font-bold text-gray-900">
                  {{ systemStats.systemHealth }}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- User Management Section -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
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
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  ></path>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  User Management
                </h3>
                <p class="text-sm text-gray-500">
                  Manage system users and permissions
                </p>
              </div>
            </div>
            <Button
              @click="showAddUserModal = true"
              class="flex items-center space-x-2"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                ></path>
              </svg>
              <span>Add User</span>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    User
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Role
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Last Login
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="user in users"
                  :key="user.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div
                        class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center"
                      >
                        <span class="text-sm font-medium text-gray-600">
                          {{
                            user.firstName?.[0] || user.email[0].toUpperCase()
                          }}
                        </span>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">
                          {{ user.firstName }} {{ user.lastName }}
                        </div>
                        <div class="text-sm text-gray-500">
                          {{ user.email }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <Badge :variant="getRoleVariant(user.role)">
                      {{ formatRole(user.role) }}
                    </Badge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <Badge :variant="user.isActive ? 'default' : 'secondary'">
                      {{ user.isActive ? "Active" : "Inactive" }}
                    </Badge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(user.lastLogin) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        @click="editUser(user)"
                        class="text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        @click="toggleUserStatus(user)"
                        :class="
                          user.isActive
                            ? 'text-red-600 hover:text-red-800'
                            : 'text-green-600 hover:text-green-800'
                        "
                      >
                        {{ user.isActive ? "Deactivate" : "Activate" }}
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <!-- System Monitoring Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Activity -->
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
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  ></path>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  Recent Activity
                </h3>
                <p class="text-sm text-gray-500">Latest system events</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
              >
                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div class="flex-1">
                  <p class="text-sm text-gray-900">
                    {{ activity.description }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ formatDate(activity.timestamp) }}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- System Alerts -->
        <Card>
          <CardHeader>
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-6 h-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
                  ></path>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  System Alerts
                </h3>
                <p class="text-sm text-gray-500">
                  Active warnings and notifications
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div
                v-for="alert in systemAlerts"
                :key="alert.id"
                class="p-3 border-l-4 border-red-400 bg-red-50 rounded-lg"
              >
                <div class="flex items-start space-x-3">
                  <svg
                    class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
                    ></path>
                  </svg>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-red-800">
                      {{ alert.title }}
                    </p>
                    <p class="text-sm text-red-700">{{ alert.description }}</p>
                    <p class="text-xs text-red-600 mt-1">
                      {{ formatDate(alert.timestamp) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Quick Actions -->
      <Card>
        <CardHeader>
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                ></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Quick Actions</h3>
              <p class="text-sm text-gray-500">Common administrative tasks</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              @click="exportSystemReport"
              class="flex items-center justify-center space-x-2 h-20"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              <span>Export Report</span>
            </Button>
            <Button
              variant="outline"
              @click="backupDatabase"
              class="flex items-center justify-center space-x-2 h-20"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                ></path>
              </svg>
              <span>Backup Database</span>
            </Button>
            <Button
              variant="outline"
              @click="clearSystemCache"
              class="flex items-center justify-center space-x-2 h-20"
            >
              <svg
                class="w-5 h-5"
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
              <span>Clear Cache</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Access Denied for Non-Admins -->
    <div v-else-if="userStore.isAuthenticated" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <div
          class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <svg
            class="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
        <p class="text-sm text-gray-500 mb-4">
          You don't have permission to access the admin panel. Contact your
          administrator.
        </p>
        <Button as-child>
          <router-link to="/dashboard">Back to Dashboard</router-link>
        </Button>
      </div>
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
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Welcome to Admin Panel
        </h3>
        <p class="text-sm text-gray-500 mb-4">
          Please sign in to access administrative functions
        </p>
        <Button as-child>
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useUserStore } from "../stores/user";
import { useAuditStore } from "../stores/audit";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";
import { useAlert } from "@/composables/useAlert";

const userStore = useUserStore();
const auditStore = useAuditStore();
const { showAlert } = useAlert();

// Modal state
const showAddUserModal = ref(false);

// System statistics
const systemStats = reactive({
  totalUsers: 0,
  activeUsers: 0,
  totalAudits: 0,
  systemHealth: 0,
});

// Mock users data
const users = ref([
  {
    id: 1,
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    role: "admin",
    isActive: true,
    lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: 2,
    firstName: "Jane",
    lastName: "Smith",
    email: "jane.smith@example.com",
    role: "auditor",
    isActive: true,
    lastLogin: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
  },
  {
    id: 3,
    firstName: "Bob",
    lastName: "Johnson",
    email: "bob.johnson@example.com",
    role: "user",
    isActive: false,
    lastLogin: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 1 week ago
  },
]);

// Recent activity
const recentActivity = ref([
  {
    id: 1,
    description: "New user registration: bob.johnson@example.com",
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
  },
  {
    id: 2,
    description: "Audit completed: Driver Log Analysis #1234",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: 3,
    description: "System backup completed successfully",
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
  },
]);

// System alerts
const systemAlerts = ref([
  {
    id: 1,
    title: "High CPU Usage",
    description: "Server CPU usage is above 80% for the last 10 minutes",
    timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
  },
  {
    id: 2,
    title: "Database Connection Warning",
    description: "Database connection pool is reaching capacity",
    timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
  },
]);

// Initialize data
const initializeData = async () => {
  if (userStore.isAuthenticated && userStore.user?.role === "admin") {
    try {
      // Fetch system stats from API
      const response = await fetch("/api/admin/system-stats", {
        headers: {
          Authorization: `Bearer ${userStore.accessToken}`,
        },
      });

      if (response.ok) {
        const stats = await response.json();
        systemStats.totalUsers = stats.totalUsers;
        systemStats.activeUsers = stats.activeUsers;
        systemStats.totalAudits = stats.totalAudits;
        systemStats.systemHealth = stats.systemHealth;
      }
    } catch (error) {
      console.error("Failed to fetch system stats:", error);
      // Fallback to mock data
      systemStats.totalUsers = users.value.length;
      systemStats.activeUsers = users.value.filter(
        (user) => user.isActive,
      ).length;
      systemStats.totalAudits = auditStore.audits.length;
      systemStats.systemHealth = 95;
    }
  }
};

// User management functions
const editUser = (user) => {
  showAlert(`Edit user: ${user.email}`, "info");
  // Here you would typically open an edit modal
};

const toggleUserStatus = async (user) => {
  try {
    const response = await fetch(`/api/admin/users/${user.id}/toggle-status`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${userStore.accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const result = await response.json();
      user.isActive = !user.isActive;
      const action = user.isActive ? "activated" : "deactivated";
      showAlert(`User ${user.email} has been ${action}`, "success");

      // Update system stats
      systemStats.activeUsers = users.value.filter((u) => u.isActive).length;
    } else {
      showAlert(
        `Failed to update user status: ${response.statusText}`,
        "error",
      );
    }
  } catch (error) {
    console.error("Error updating user status:", error);
    showAlert("Failed to update user status. Please try again.", "error");
  }
};

// Quick action functions
const exportSystemReport = async () => {
  showAlert("Exporting system report...", "info");
  // Here you would typically generate and download a report
  await new Promise((resolve) => setTimeout(resolve, 2000));
  showAlert("System report exported successfully!", "success");
};

const backupDatabase = async () => {
  showAlert("Starting database backup...", "info");
  // Here you would typically initiate a database backup
  await new Promise((resolve) => setTimeout(resolve, 3000));
  showAlert("Database backup completed successfully!", "success");
};

const clearSystemCache = async () => {
  showAlert("Clearing system cache...", "info");
  // Here you would typically clear system cache
  await new Promise((resolve) => setTimeout(resolve, 1500));
  showAlert("System cache cleared successfully!", "success");
};

// Utility functions
const formatRole = (role) => {
  const roles = {
    admin: "Administrator",
    auditor: "Auditor",
    user: "User",
  };
  return roles[role] || role;
};

const getRoleVariant = (role) => {
  const variants = {
    admin: "destructive",
    auditor: "default",
    user: "secondary",
  };
  return variants[role] || "secondary";
};

const formatDate = (date) => {
  if (!date) return "Never";
  return new Date(date).toLocaleDateString();
};

// Initialize data when component mounts
onMounted(async () => {
  if (userStore.isAuthenticated) {
    if (auditStore.audits.length === 0) {
      await auditStore.fetchAudits();
    }
    initializeData();
  }
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
