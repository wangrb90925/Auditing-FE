<template>
  <div class="space-y-8">
    <!-- Enhanced Header with better visual hierarchy -->
    <div class="relative">
      <!-- Background decoration -->
      <div
        class="absolute inset-0 bg-gradient-to-r from-blue-50/50 via-transparent to-purple-50/50 rounded-3xl -z-10"
      ></div>

      <div
        class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6 p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-100/50 shadow-sm"
      >
        <div class="space-y-3">
          <div class="flex items-center space-x-3">
            <div
              class="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <ChartIcon class="w-7 h-7 text-white" />
            </div>
            <div>
              <h1
                class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
              >
                FMCSA Compliance Dashboard
              </h1>
              <p class="text-gray-600 text-lg font-medium">
                Hours-of-Service (HOS) audit overview and violation tracking
              </p>
            </div>
          </div>
        </div>

        <Button
          v-if="userStore.isAuthenticated"
          as-child
          class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 rounded-2xl px-8 py-4 text-lg font-semibold"
        >
          <router-link to="/upload" class="flex items-center">
            <PlusIcon class="w-5 h-5 mr-3" />
            New HOS Audit
          </router-link>
        </Button>
      </div>
    </div>

    <!-- Enhanced Stats Cards with better animations -->
    <div
      v-if="userStore.isAuthenticated"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      <Card
        class="group bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200/50 dark:border-blue-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
      >
        <!-- Animated background -->
        <div
          class="absolute inset-0 bg-gradient-to-r from-blue-400/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        ></div>

        <CardContent class="p-6 relative z-10">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
              >
                <ChartIcon class="w-7 h-7 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p
                class="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1"
              >
                Total Audits
              </p>
              <p class="text-4xl font-bold text-blue-900 dark:text-blue-100">
                {{ audits.length }}
              </p>
              <p class="text-xs text-blue-500/70 mt-1">All time audits</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="group bg-gradient-to-br from-amber-50 to-amber-100/50 dark:from-amber-950/50 dark:to-amber-900/30 border-amber-200/50 dark:border-amber-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-amber-400/10 to-amber-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        ></div>

        <CardContent class="p-6 relative z-10">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
              >
                <ClockIcon class="w-7 h-7 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p
                class="text-sm font-medium text-amber-600 dark:text-amber-400 mb-1"
              >
                Pending Review
              </p>
              <p class="text-4xl font-bold text-amber-900 dark:text-amber-100">
                {{ auditStore.pendingAudits.length }}
              </p>
              <p class="text-xs text-amber-500/70 mt-1">Awaiting review</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="group bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/50 dark:to-green-900/30 border-green-200/50 dark:border-green-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-green-400/10 to-green-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        ></div>

        <CardContent class="p-6 relative z-10">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
              >
                <CheckIcon class="w-7 h-7 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p
                class="text-sm font-medium text-green-600 dark:text-green-400 mb-1"
              >
                HOS Compliant
              </p>
              <p class="text-4xl font-bold text-green-900 dark:text-green-100">
                {{ auditStore.completedAudits.length }}
              </p>
              <p class="text-xs text-green-500/70 mt-1">Compliant audits</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="group bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/50 dark:to-red-900/30 border-red-200/50 dark:border-red-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-red-400/10 to-red-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        ></div>

        <CardContent class="p-6 relative z-10">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-14 h-14 bg-gradient-to-br from-red-500 to-red-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
              >
                <WarningIcon class="w-7 h-7 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p
                class="text-sm font-medium text-red-600 dark:text-red-400 mb-1"
              >
                HOS Violations
              </p>
              <p class="text-4xl font-bold text-red-900 dark:text-red-100">
                {{ totalViolations }}
              </p>
              <p class="text-xs text-red-500/70 mt-1">Total violations</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Enhanced No Data Messages -->
    <div v-else-if="!userStore.isAuthenticated" class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <ChartIcon class="w-10 h-10 text-blue-600" />
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">
          Welcome to FMCSA Compliance Dashboard
        </h3>
        <p class="text-gray-600 mb-6 leading-relaxed">
          Please sign in to view your audit statistics and compliance data
        </p>
        <Button
          as-child
          class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg rounded-xl px-8 py-3"
        >
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>

    <div v-else class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-amber-100 to-orange-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <ChartIcon class="w-10 h-10 text-amber-600" />
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">
          No Audit Data Available
        </h3>
        <p class="text-gray-600 mb-6 leading-relaxed">
          Start by uploading driver logs for your first HOS compliance audit
        </p>
        <Button
          as-child
          class="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 shadow-lg rounded-xl px-8 py-3"
        >
          <router-link to="/upload">Upload Driver Logs</router-link>
        </Button>
      </div>
    </div>

    <!-- Enhanced Recent Audits Section -->
    <Card
      class="bg-white/80 backdrop-blur-sm border-gray-100/50 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden"
    >
      <CardHeader
        class="bg-gradient-to-r from-gray-50 to-gray-100/50 border-b border-gray-200/50"
      >
        <div class="flex justify-between items-center">
          <div class="space-y-1">
            <h2 class="text-2xl font-bold text-gray-900">Recent HOS Audits</h2>
            <p class="text-gray-600 font-medium">
              Latest FMCSA compliance assessments
            </p>
          </div>
          <Button
            v-if="audits.length > 0"
            variant="outline"
            as-child
            class="rounded-xl border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all duration-300"
          >
            <router-link to="/audits" class="flex items-center">
              <span>View all</span>
              <svg
                class="w-4 h-4 ml-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                ></path>
              </svg>
            </router-link>
          </Button>
        </div>
      </CardHeader>

      <CardContent class="p-0">
        <!-- Enhanced table with better styling -->
        <div v-if="audits.length > 0" class="overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200/50">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100/50">
              <tr>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  Driver
                </th>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  Type
                </th>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  HOS Violations
                </th>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  Date
                </th>
                <th
                  class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200/30">
              <!-- Enhanced audit rows with better hover effects -->
              <tr
                v-for="(audit, index) in recentAudits"
                :key="audit.id"
                class="hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 transition-all duration-300 group"
                :style="{ animationDelay: `${index * 100}ms` }"
              >
                <td class="px-8 py-5 whitespace-nowrap">
                  <div class="flex items-center">
                    <div
                      class="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-300"
                    >
                      <span class="text-sm font-semibold text-blue-600">{{
                        audit.driverName.charAt(0).toUpperCase()
                      }}</span>
                    </div>
                    <div>
                      <div
                        class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-300"
                      >
                        {{ audit.driverName }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ audit.files?.length || 0 }} files
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-8 py-5 whitespace-nowrap">
                  <Badge
                    variant="secondary"
                    class="rounded-full px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors duration-300"
                  >
                    {{ formatDriverType(audit.driverType) }}
                  </Badge>
                </td>
                <td class="px-8 py-5 whitespace-nowrap">
                  <Badge
                    :variant="getStatusVariant(audit.status)"
                    class="rounded-full px-3 py-1 text-xs font-medium shadow-sm"
                  >
                    {{ formatStatus(audit.status) }}
                  </Badge>
                </td>
                <td class="px-8 py-5 whitespace-nowrap">
                  <div class="flex items-center">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center mr-2"
                      :class="
                        audit.violations > 0
                          ? 'bg-red-100 text-red-600'
                          : 'bg-green-100 text-green-600'
                      "
                    >
                      <span class="text-sm font-bold">{{
                        audit.violations || 0
                      }}</span>
                    </div>
                    <span class="text-sm text-gray-600">{{
                      audit.violations > 0 ? "violations" : "compliant"
                    }}</span>
                  </div>
                </td>
                <td class="px-8 py-5 whitespace-nowrap">
                  <div class="text-sm text-gray-900 font-medium">
                    {{ formatDate(audit.createdAt) }}
                  </div>
                  <div class="text-xs text-gray-500">Audit date</div>
                </td>
                <td class="px-8 py-5 whitespace-nowrap">
                  <div class="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      as-child
                      class="rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-all duration-300 group-hover:scale-105"
                    >
                      <router-link
                        :to="`/audit/${audit.id}`"
                        class="flex items-center"
                      >
                        <svg
                          class="w-4 h-4 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                          ></path>
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                          ></path>
                        </svg>
                        View
                      </router-link>
                    </Button>
                    <Button
                      v-if="audit.status === 'completed'"
                      variant="outline"
                      size="sm"
                      @click="downloadReport(audit.id)"
                      class="rounded-lg border-gray-300 hover:bg-green-50 hover:border-green-300 hover:text-green-600 transition-all duration-300 group-hover:scale-105"
                    >
                      <DownloadIcon class="w-4 h-4 mr-1" />
                      Export
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Enhanced no data message -->
        <div v-else class="text-center py-16">
          <div class="flex flex-col items-center space-y-4">
            <div class="relative">
              <div
                class="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center shadow-lg"
              >
                <DocumentIcon class="w-10 h-10 text-gray-400" />
              </div>
              <div
                class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full animate-pulse"
              ></div>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">
                No audits found
              </h3>
              <p class="text-gray-600">
                Start by uploading driver logs for your first HOS audit
              </p>
            </div>
            <Button
              as-child
              variant="outline"
              class="mt-4 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 text-blue-700 hover:from-blue-100 hover:to-purple-100 rounded-xl px-6 py-2"
            >
              <router-link to="/upload">Upload Driver Logs</router-link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Enhanced Quick Actions with better visual appeal -->
    <div
      v-if="userStore.isAuthenticated"
      class="grid grid-cols-1 md:grid-cols-3 gap-8 !mb-20"
    >
      <Card
        class="bg-gradient-to-br from-blue-50/80 to-blue-100/60 border-blue-200/50 hover:shadow-2xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
      >
        <!-- Animated background elements -->
        <div
          class="absolute top-0 right-0 w-32 h-32 bg-blue-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
        ></div>
        <div
          class="absolute bottom-0 left-0 w-24 h-24 bg-blue-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
        ></div>

        <CardContent class="p-8 relative z-10">
          <div class="text-center">
            <div
              class="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center mb-6 shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500"
            >
              <UploadIcon class="w-10 h-10 text-white" />
            </div>
            <h3
              class="text-2xl font-bold text-gray-900 mb-4 group-hover:text-blue-600 transition-colors duration-300"
            >
              Upload Driver Logs
            </h3>
            <p class="text-gray-600 mb-8 leading-relaxed">
              Upload ELD logs, fuel receipts, and BOLs for AI-powered FMCSA
              compliance auditing
            </p>
            <Button
              as-child
              class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-xl hover:shadow-2xl rounded-2xl py-4 text-lg font-semibold transform group-hover:scale-105 transition-all duration-300"
            >
              <router-link to="/upload">Start HOS Audit</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-amber-50/80 to-amber-100/60 border-amber-200/50 hover:shadow-2xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
      >
        <div
          class="absolute top-0 right-0 w-32 h-32 bg-amber-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
        ></div>
        <div
          class="absolute bottom-0 left-0 w-24 h-24 bg-amber-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
        ></div>

        <CardContent class="p-8 relative z-10">
          <div class="text-center">
            <div
              class="mx-auto w-20 h-20 bg-gradient-to-br from-amber-500 to-amber-600 rounded-3xl flex items-center justify-center mb-6 shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500"
            >
              <InfoIcon class="w-10 h-10 text-white" />
            </div>
            <h3
              class="text-2xl font-bold text-gray-900 mb-4 group-hover:text-amber-600 transition-colors duration-300"
            >
              Audit History
            </h3>
            <p class="text-gray-600 mb-8 leading-relaxed">
              Review past HOS audits and track compliance trends across driver
              types and exemptions
            </p>
            <Button
              variant="outline"
              as-child
              class="w-full rounded-2xl border-amber-300 text-amber-700 hover:bg-amber-50 hover:border-amber-400 py-4 text-lg font-semibold transform group-hover:scale-105 transition-all duration-300"
            >
              <router-link to="/audits">View History</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-green-50/80 to-green-100/60 border-green-200/50 hover:shadow-2xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
      >
        <div
          class="absolute top-0 right-0 w-32 h-32 bg-green-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
        ></div>
        <div
          class="absolute bottom-0 left-0 w-24 h-24 bg-green-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
        ></div>

        <CardContent class="p-8 relative z-10">
          <div class="text-center">
            <div
              class="mx-auto w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-3xl flex items-center justify-center mb-6 shadow-xl group-hover:shadow-2xl group-hover:scale-110 transition-all duration-500"
            >
              <DocumentIcon class="w-10 h-10 text-white" />
            </div>
            <h3
              class="text-2xl font-bold text-gray-900 mb-4 group-hover:text-green-600 transition-colors duration-300"
            >
              Audit Reports
            </h3>
            <p class="text-gray-600 mb-8 leading-relaxed">
              Access detailed FMCSA compliance reports with violation analysis
              and export capabilities
            </p>
            <Button
              variant="outline"
              as-child
              class="w-full rounded-2xl border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400 py-4 text-lg font-semibold transform group-hover:scale-105 transition-all duration-300"
            >
              <router-link to="/reports">Generate Reports</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useAuditStore } from "../stores/audit";
import { useUserStore } from "../stores/user";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";
import {
  PlusIcon,
  ChartIcon,
  ClockIcon,
  CheckIcon,
  WarningIcon,
  DownloadIcon,
  UploadIcon,
  DocumentIcon,
  InfoIcon,
} from "@/assets/icons";

const auditStore = useAuditStore();
const userStore = useUserStore();

// Initialize data - try to fetch from API if authenticated
const initializeData = async () => {
  // Check if user is authenticated
  if (!userStore.isAuthenticated) {
    console.log("User not authenticated, no data to display");
    return;
  }

  try {
    // Try to fetch real data from API
    await auditStore.fetchAudits();
  } catch (error) {
    console.log("API not available or authentication failed");
    // Don't initialize any data, let the UI show "no data" message
  }
};

// Watch for authentication state changes
watch(
  () => userStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      // User just logged in, try to fetch real data
      initializeData();
    }
    // If user logs out, no need to do anything - audits will be empty
  }
);

// Initialize data when component mounts
initializeData();

const audits = computed(() => {
  return auditStore.audits || [];
});

const totalViolations = computed(() => {
  if (!audits.value || !Array.isArray(audits.value)) {
    return 0;
  }
  return audits.value.reduce((total, audit) => {
    return total + (audit.violations || 0);
  }, 0);
});

const recentAudits = computed(() => {
  if (!audits.value || !Array.isArray(audits.value)) {
    return [];
  }
  const sortedAudits = [...audits.value].sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
  );
  return sortedAudits.slice(0, 5);
});

const formatDriverType = (type) => {
  const types = {
    "long-haul": "Long Haul",
    "short-haul": "Short Haul",
    exemption: "Exemption",
  };
  return types[type] || type;
};

const formatStatus = (status) => {
  const statuses = {
    pending: "Pending Review",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  };
  return statuses[status] || status;
};

const getStatusVariant = (status) => {
  const variants = {
    pending: "secondary",
    processing: "default",
    completed: "default",
    failed: "destructive",
  };
  return variants[status] || status;
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const downloadReport = (auditId) => {
  const audit = auditStore.getAuditById(auditId);
  if (!audit) return;

  // Create CSV content for FMCSA compliance report
  const csvContent = [
    [
      "Driver Name",
      "Driver Type",
      "Status",
      "HOS Violations",
      "Compliance Score",
      "Audit Date",
    ],
    [
      audit.driverName,
      formatDriverType(audit.driverType),
      formatStatus(audit.status),
      audit.violations || 0,
      audit.summary?.complianceScore || "N/A",
      formatDate(audit.createdAt),
    ],
  ]
    .map((row) => row.join(","))
    .join("\n");

  // Create and download file
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `fmcsa-audit-${auditId}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};
</script>

<style scoped>
/* Enhanced animations and transitions */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}

/* Stagger animation for table rows */
tbody tr {
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
}

tbody tr:nth-child(1) {
  animation-delay: 0.1s;
}
tbody tr:nth-child(2) {
  animation-delay: 0.2s;
}
tbody tr:nth-child(3) {
  animation-delay: 0.3s;
}
tbody tr:nth-child(4) {
  animation-delay: 0.4s;
}
tbody tr:nth-child(5) {
  animation-delay: 0.5s;
}

/* Enhanced hover effects */
.group:hover .group-hover\:scale-105 {
  transform: scale(1.05);
}

.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced focus states */
button:focus,
a:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
