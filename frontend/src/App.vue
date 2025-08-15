<template>
  <div id="app" class="min-h-screen bg-background">
    <nav
      v-if="isAuthenticated"
      class="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo and Brand -->
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center">
              <div class="flex items-center space-x-3">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center shadow-lg"
                >
                  <LogoIcon class="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <h1 class="text-xl font-bold text-foreground">
                    AI Auditing Agent
                  </h1>
                  <p class="text-xs text-muted-foreground">
                    Compliance Made Simple
                  </p>
                </div>
              </div>
            </div>

            <!-- Navigation Links -->
            <div class="hidden md:ml-10 md:flex md:space-x-2">
              <Button
                variant="ghost"
                as-child
                class="px-4 py-2 h-10 rounded-lg transition-all duration-200"
                :class="{
                  'bg-primary/10 text-primary border border-primary/20':
                    $route.path === '/dashboard',
                  'text-muted-foreground hover:text-foreground hover:bg-muted/50':
                    $route.path !== '/dashboard',
                }"
              >
                <router-link
                  to="/dashboard"
                  class="flex items-center space-x-2"
                >
                  <DashboardIcon class="w-4 h-4" />
                  <span class="font-medium">Dashboard</span>
                </router-link>
              </Button>

              <Button
                variant="ghost"
                as-child
                class="px-4 py-2 h-10 rounded-lg transition-all duration-200"
                :class="{
                  'bg-primary/10 text-primary border border-primary/20':
                    $route.path === '/upload',
                  'text-muted-foreground hover:text-foreground hover:bg-muted/50':
                    $route.path !== '/upload',
                }"
              >
                <router-link to="/upload" class="flex items-center space-x-2">
                  <UploadIcon class="w-4 h-4" />
                  <span class="font-medium">Upload Files</span>
                </router-link>
              </Button>

              <Button
                variant="ghost"
                as-child
                class="px-4 py-2 h-10 rounded-lg transition-all duration-200"
                :class="{
                  'bg-primary/10 text-primary border border-primary/20':
                    $route.path === '/audits',
                  'text-muted-foreground hover:text-foreground hover:bg-muted/50':
                    $route.path !== '/audits',
                }"
              >
                <router-link to="/audits" class="flex items-center space-x-2">
                  <AuditHistoryIcon class="w-4 h-4" />
                  <span class="font-medium">Audit History</span>
                </router-link>
              </Button>
            </div>
          </div>

          <!-- Right Side: Theme Toggle and User Menu -->
          <div class="flex items-center space-x-4">
            <!-- Theme Toggle -->
            <Button
              variant="ghost"
              size="sm"
              @click="themeStore.toggleTheme"
              class="text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-lg transition-all duration-200"
              :title="
                themeStore.theme === 'light'
                  ? 'Switch to dark mode'
                  : 'Switch to light mode'
              "
            >
              <SunIcon v-if="themeStore.theme === 'light'" class="w-4 h-4" />
              <MoonIcon v-else class="w-4 h-4" />
            </Button>

            <!-- User Menu -->
            <UserProfile />
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content with proper spacing to prevent layout shift -->
    <main
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
      :class="{ 'py-8': isAuthenticated, 'py-0': !isAuthenticated }"
    >
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "./stores/user";
import { useThemeStore } from "./stores/theme";
import Button from "@/components/ui/button.vue";
import UserProfile from "@/components/UserProfile.vue";
import {
  LogoIcon,
  DashboardIcon,
  UploadIcon,
  AuditHistoryIcon,
  SunIcon,
  MoonIcon,
} from "@/assets/icons";

const router = useRouter();
const userStore = useUserStore();
const themeStore = useThemeStore();

const isAuthenticated = computed(() => userStore.isAuthenticated);

// Logout function is now handled in UserProfile component
</script>
