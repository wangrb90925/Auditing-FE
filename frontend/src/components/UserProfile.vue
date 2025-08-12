<template>
  <div class="relative">
    <!-- User Menu Button -->
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg p-2"
    >
      <div
        class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center"
      >
        <span class="text-sm font-medium text-primary-600">
          {{ userInitials }}
        </span>
      </div>
      <div class="hidden md:block text-left">
        <p class="text-sm font-medium text-gray-900">
          {{ user?.first_name }} {{ user?.last_name }}
        </p>
        <p class="text-xs text-gray-500 capitalize">{{ user?.role }}</p>
      </div>
      <svg
        class="w-4 h-4 text-gray-400"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50"
    >
      <div class="py-1">
        <!-- User Info -->
        <div class="px-4 py-2 border-b border-gray-100">
          <p class="text-sm font-medium text-gray-900">
            {{ user?.first_name }} {{ user?.last_name }}
          </p>
          <p class="text-xs text-gray-500">{{ user?.email }}</p>
          <p class="text-xs text-gray-500 capitalize">{{ user?.role }}</p>
        </div>

        <!-- Menu Items -->
        <button
          @click="handleProfile"
          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
        >
          <div class="flex items-center space-x-2">
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <span>Profile</span>
          </div>
        </button>

        <button
          v-if="isAdmin"
          @click="handleAdminPanel"
          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
        >
          <div class="flex items-center space-x-2">
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
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            <span>Admin Panel</span>
          </div>
        </button>

        <button
          @click="handleLogout"
          class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
        >
          <div class="flex items-center space-x-2">
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
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            <span>Sign Out</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";

const router = useRouter();
const userStore = useUserStore();

const isOpen = ref(false);

const user = computed(() => userStore.user);
const isAdmin = computed(() => userStore.isAdmin);

const userInitials = computed(() => {
  if (!user.value?.first_name || !user.value?.last_name) {
    return user.value?.username?.charAt(0).toUpperCase() || "U";
  }
  return `${user.value.first_name.charAt(0)}${user.value.last_name.charAt(0)}`.toUpperCase();
});

const handleProfile = () => {
  isOpen.value = false;
  // TODO: Navigate to profile page when created
  console.log("Navigate to profile page");
};

const handleAdminPanel = () => {
  isOpen.value = false;
  // TODO: Navigate to admin panel when created
  console.log("Navigate to admin panel");
};

const handleLogout = () => {
  isOpen.value = false;
  userStore.logout();
  router.push("/login");
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest(".relative")) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>


