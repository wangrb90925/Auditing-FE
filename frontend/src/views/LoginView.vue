<template>
  <div
    class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <div>
        <div
          class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 shadow-soft"
        >
          <svg
            class="h-8 w-8 text-primary-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          AI Auditing Agent
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Sign in to access the CDL Manager audit system
        </p>
      </div>

      <Card class="shadow-medium">
        <CardContent class="p-8">
          <form class="space-y-6" @submit.prevent="handleLogin">
            <div class="space-y-4">
              <div>
                <Label for="username">Username</Label>
                <Input
                  id="username"
                  v-model="credentials.username"
                  name="username"
                  type="text"
                  required
                  placeholder="Enter your username"
                />
              </div>
              <div>
                <Label for="password">Password</Label>
                <Input
                  id="password"
                  v-model="credentials.password"
                  name="password"
                  type="password"
                  required
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div v-if="error" class="text-center">
              <p class="text-danger-600 text-sm">{{ error }}</p>
            </div>

            <div>
              <Button
                type="submit"
                :disabled="isLoading"
                class="w-full"
                size="lg"
              >
                <svg
                  v-if="isLoading"
                  class="animate-spin -ml-1 mr-3 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                {{ isLoading ? "Signing in..." : "Sign in" }}
              </Button>
            </div>

            <div class="text-center">
              <p class="text-xs text-gray-500 mb-4">
                Demo credentials: admin / password
              </p>
              <p class="text-sm text-gray-600">
                Don't have an account?
                <router-link
                  to="/signup"
                  class="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign up here
                </router-link>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import Button from "@/components/ui/button.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Card from "@/components/ui/card.vue";
import CardContent from "@/components/ui/card-content.vue";

const router = useRouter();
const userStore = useUserStore();

const credentials = ref({
  username: "",
  password: "",
});

const isLoading = ref(false);
const error = ref("");

const handleLogin = async () => {
  isLoading.value = true;
  error.value = "";

  try {
    const result = await userStore.login(credentials.value);
    if (result.success) {
      router.push("/dashboard");
    } else {
      error.value = result.error || "Login failed";
    }
  } catch (err) {
    error.value = "An unexpected error occurred";
  } finally {
    isLoading.value = false;
  }
};
</script>
