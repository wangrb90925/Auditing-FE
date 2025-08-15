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
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create Account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Join the AI Auditing Agent platform
        </p>
      </div>

      <Card class="shadow-medium">
        <CardContent class="p-8">
          <form class="space-y-6" @submit.prevent="handleSignup">
            <div class="space-y-4">
              <div>
                <Label for="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  v-model="formData.fullName"
                  name="fullName"
                  type="text"
                  required
                  placeholder="Enter your full name"
                />
              </div>

              <div>
                <Label for="email">Email Address</Label>
                <Input
                  id="email"
                  v-model="formData.email"
                  name="email"
                  type="email"
                  required
                  placeholder="Enter your email address"
                />
              </div>

              <div>
                <Label for="username">Username</Label>
                <Input
                  id="username"
                  v-model="formData.username"
                  name="username"
                  type="text"
                  required
                  placeholder="Choose a username"
                />
              </div>

              <div>
                <Label for="password">Password</Label>
                <Input
                  id="password"
                  v-model="formData.password"
                  name="password"
                  type="password"
                  required
                  placeholder="Create a password"
                />
              </div>

              <div>
                <Label for="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  v-model="formData.confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  placeholder="Confirm your password"
                />
              </div>

              <div>
                <Label for="role">Role</Label>
                <Select id="role" v-model="formData.role" name="role" required>
                  <option value="">Select your role</option>
                  <option value="auditor">Auditor</option>
                  <option value="admin">Admin</option>
                </Select>
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
                {{ isLoading ? "Creating account..." : "Create Account" }}
              </Button>
            </div>

            <div class="text-center">
              <p class="text-sm text-gray-600">
                Already have an account?
                <router-link
                  to="/login"
                  class="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign in here
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
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import Button from "@/components/ui/button.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import Card from "@/components/ui/card.vue";
import CardContent from "@/components/ui/card-content.vue";

const router = useRouter();
const userStore = useUserStore();

const formData = reactive({
  fullName: "",
  email: "",
  username: "",
  password: "",
  confirmPassword: "",
  role: "",
});

const isLoading = ref(false);
const error = ref("");

const validateForm = () => {
  if (!formData.fullName.trim()) {
    error.value = "Full name is required";
    return false;
  }

  if (!formData.email.trim()) {
    error.value = "Email is required";
    return false;
  }

  if (!formData.username.trim()) {
    error.value = "Username is required";
    return false;
  }

  if (formData.password !== formData.confirmPassword) {
    error.value = "Passwords do not match";
    return false;
  }

  if (formData.password.length < 6) {
    error.value = "Password must be at least 6 characters long";
    return false;
  }

  if (!formData.role) {
    error.value = "Please select a role";
    return false;
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.email)) {
    error.value = "Please enter a valid email address";
    return false;
  }

  return true;
};

const handleSignup = async () => {
  isLoading.value = true;
  error.value = "";

  if (!validateForm()) {
    isLoading.value = false;
    return;
  }

  try {
    const result = await userStore.signup(formData);

    if (result.success) {
      router.push("/dashboard");
    } else {
      error.value = result.error || "Signup failed";
    }
  } catch (err) {
    error.value = "An unexpected error occurred";
  } finally {
    isLoading.value = false;
  }
};
</script>
