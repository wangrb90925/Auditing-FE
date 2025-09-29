<template>
  <div class="space-y-6">
    <!-- Enhanced Header with better visual hierarchy -->
    <div class="relative">
      <!-- Background decoration -->
      <div
        class="absolute inset-0 bg-gradient-to-r from-indigo-50/50 via-transparent to-purple-50/50 rounded-3xl -z-10"
      ></div>

      <div
        class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6 p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-100/50 shadow-sm"
      >
        <div class="space-y-3">
          <div class="flex items-center space-x-3">
            <div
              class="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <svg
                class="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
            </div>
            <div>
              <h1
                class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
              >
                Audit Reports
              </h1>
              <p class="text-gray-600 text-lg font-medium">
                Generate comprehensive audit reports and analytics
              </p>
            </div>
          </div>
        </div>

        <div
          v-if="userStore.isAuthenticated"
          class="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3"
        >
          <Button
            variant="outline"
            @click="generateReport"
            class="flex items-center space-x-2 rounded-xl border-indigo-300 text-indigo-700 hover:bg-indigo-50 hover:border-indigo-400 transition-all duration-300 px-6 py-3"
          >
            <DocumentIcon class="w-5 h-5" />
            <span class="font-semibold">Generate Report</span>
          </Button>
          <Button
            variant="outline"
            @click="exportToPDF"
            class="flex items-center space-x-2 rounded-xl border-purple-300 text-purple-700 hover:bg-purple-50 hover:border-purple-400 transition-all duration-300 px-6 py-3"
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
            <span class="font-semibold">Export Summary</span>
          </Button>
          <Button
            variant="outline"
            @click="exportAllToCSV"
            class="flex items-center space-x-2 rounded-xl border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400 transition-all duration-300 px-6 py-3"
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
                d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
            <span class="font-semibold">Export CSV</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Enhanced Welcome Message for Unauthenticated Users -->
    <div v-if="!userStore.isAuthenticated" class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <DocumentIcon class="w-10 h-10 text-indigo-600" />
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">
          Welcome to Audit Reports
        </h3>
        <p class="text-gray-600 mb-6 leading-relaxed">
          Please sign in to generate and view audit reports
        </p>
        <Button
          as-child
          class="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg rounded-xl px-8 py-3"
        >
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>

    <!-- Main Content for Authenticated Users -->
    <div v-else>
      <!-- Enhanced Report Generation Section -->
      <Card
        class="bg-white/80 backdrop-blur-sm border-gray-100/50 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden mb-8"
      >
        <CardHeader
          class="bg-gradient-to-r from-indigo-50 to-indigo-100/50 border-b border-indigo-200/50"
        >
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center"
            >
              <svg
                class="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900">Generate New Report</h3>
          </div>
        </CardHeader>
        <CardContent class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="space-y-3">
              <Label
                for="reportType"
                class="text-sm font-semibold text-gray-700"
                >Report Type</Label
              >
              <Select
                id="reportType"
                v-model="reportConfig.type"
                class="w-full h-12 text-lg border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-xl transition-all duration-300"
              >
                <option value="compliance">Compliance Summary</option>
                <option value="violations">Violations Analysis</option>
                <option value="trends">Trends Report</option>
                <option value="comprehensive">Comprehensive Audit</option>
              </Select>
            </div>
            <div class="space-y-3">
              <Label for="dateRange" class="text-sm font-semibold text-gray-700"
                >Date Range</Label
              >
              <Select
                id="dateRange"
                v-model="reportConfig.dateRange"
                class="w-full h-12 text-lg border-gray-300 focus:border-purple-500 focus:ring-purple-500 rounded-xl transition-all duration-300"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="1y">Last Year</option>
                <option value="custom">Custom Range</option>
              </Select>
            </div>
            <div class="space-y-3">
              <Label
                for="driverFilter"
                class="text-sm font-semibold text-gray-700"
                >Driver Filter</Label
              >
              <Select
                id="driverFilter"
                v-model="reportConfig.driverFilter"
                class="w-full h-12 text-lg border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-xl transition-all duration-300"
              >
                <option value="all">All Drivers</option>
                <option value="specific">Specific Driver</option>
                <option value="team">Team Drivers</option>
              </Select>
            </div>
          </div>
          <div class="mt-8 flex justify-end">
            <Button
              @click="generateReport"
              :disabled="isGenerating"
              class="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-xl hover:shadow-2xl rounded-2xl px-8 py-4 text-lg font-semibold transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                v-if="isGenerating"
                class="animate-spin -ml-1 mr-3 h-6 w-6 text-white"
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
              {{ isGenerating ? "Generating..." : "Generate Report" }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Enhanced Analytics Dashboard -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card
          class="group bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/50 dark:to-green-900/30 border-green-200/50 dark:border-green-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
        >
          <!-- Animated background -->
          <div
            class="absolute inset-0 bg-gradient-to-r from-green-400/10 to-green-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          ></div>

          <CardContent class="p-6 relative z-10">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div
                  class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
                >
                  <svg
                    class="w-7 h-7 text-white"
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
              </div>
              <div class="ml-4">
                <p
                  class="text-sm font-medium text-green-600 dark:text-green-400 mb-1"
                >
                  Compliance Rate
                </p>
                <p
                  class="text-4xl font-bold text-green-900 dark:text-green-100"
                >
                  87.5%
                </p>
                <p class="text-xs text-green-500/70 mt-1">Above target</p>
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
                  <svg
                    class="w-7 h-7 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                    ></path>
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <p
                  class="text-sm font-medium text-red-600 dark:text-red-400 mb-1"
                >
                  Total Violations
                </p>
                <p class="text-4xl font-bold text-red-900 dark:text-red-100">
                  24
                </p>
                <p class="text-xs text-red-500/70 mt-1">This month</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="group bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200/50 dark:border-blue-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
        >
          <div
            class="absolute inset-0 bg-gradient-to-r from-blue-400/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          ></div>

          <CardContent class="p-6 relative z-10">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div
                  class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
                >
                  <svg
                    class="w-7 h-7 text-white"
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
              </div>
              <div class="ml-4">
                <p
                  class="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1"
                >
                  Audits This Month
                </p>
                <p class="text-4xl font-bold text-blue-900 dark:text-blue-100">
                  156
                </p>
                <p class="text-xs text-blue-500/70 mt-1">+12% vs last month</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="group bg-gradient-to-br from-yellow-50 to-yellow-100/50 dark:from-yellow-950/50 dark:to-yellow-900/30 border-yellow-200/50 dark:border-yellow-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
        >
          <div
            class="absolute inset-0 bg-gradient-to-r from-yellow-400/10 to-yellow-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          ></div>

          <CardContent class="p-6 relative z-10">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div
                  class="w-14 h-14 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
                >
                  <svg
                    class="w-7 h-7 text-white"
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
              </div>
              <div class="ml-4">
                <p
                  class="text-sm font-medium text-yellow-600 dark:text-yellow-400 mb-1"
                >
                  Risk Score
                </p>
                <p
                  class="text-4xl font-bold text-yellow-900 dark:text-yellow-100"
                >
                  Medium
                </p>
                <p class="text-xs text-yellow-500/70 mt-1">Acceptable level</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Enhanced Recent Reports -->
      <Card
        class="bg-white/80 backdrop-blur-sm border-gray-100/50 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden"
      >
        <CardHeader
          class="bg-gradient-to-r from-blue-50 to-blue-100/50 border-b border-blue-200/50"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900">Recent Reports</h3>
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-6">
          <div class="space-y-4">
            <div
              v-for="(report, index) in recentReports"
              :key="report.id"
              class="flex items-center justify-between p-6 bg-gradient-to-r from-gray-50 to-gray-100/50 rounded-xl border border-gray-200/50 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 hover:shadow-md transition-all duration-300 group"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="flex items-center space-x-4">
                <div
                  class="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300"
                >
                  <DocumentIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4
                    class="font-semibold text-gray-900 text-lg group-hover:text-blue-600 transition-colors duration-300"
                  >
                    {{ report.title }}
                  </h4>
                  <p class="text-gray-600 mb-1">{{ report.description }}</p>
                  <p class="text-sm text-gray-500">
                    Generated {{ report.generatedAt }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <Button
                  variant="outline"
                  size="sm"
                  @click="viewReport(report.id)"
                  class="rounded-lg hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-all duration-300 group-hover:scale-105"
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
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  @click="downloadReport(report.id)"
                  class="rounded-lg hover:bg-green-50 hover:text-green-600 hover:border-green-300 transition-all duration-300 group-hover:scale-105"
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
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    ></path>
                  </svg>
                  Download
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { useAuditStore } from "../stores/audit";
import { useAlert } from "../composables/useAlert";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import { DocumentIcon } from "@/assets/icons";

const router = useRouter();
const userStore = useUserStore();
const auditStore = useAuditStore();
const { showSuccess, showError } = useAlert();

// Report configuration
const reportConfig = ref({
  type: "compliance",
  dateRange: "30d",
  driverFilter: "all",
});

const isGenerating = ref(false);

// Mock recent reports data
const recentReports = ref([
  {
    id: 1,
    title: "Monthly Compliance Summary",
    description: "Comprehensive compliance report for August 2024",
    generatedAt: "2 hours ago",
    type: "compliance",
  },
  {
    id: 2,
    title: "Violations Analysis Report",
    description: "Detailed analysis of HOS violations",
    generatedAt: "1 day ago",
    type: "violations",
  },
  {
    id: 3,
    title: "Q3 Trends Report",
    description: "Quarterly trends and patterns analysis",
    generatedAt: "3 days ago",
    type: "trends",
  },
]);

const generateReport = async () => {
  isGenerating.value = true;
  try {
    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    showSuccess(
      "Report Generated",
      `${reportConfig.value.type} report has been generated successfully!`
    );

    // Add to recent reports
    const newReport = {
      id: Date.now(),
      title: `${reportConfig.value.type.charAt(0).toUpperCase() + reportConfig.value.type.slice(1)} Report`,
      description: `Generated ${reportConfig.value.type} report for ${reportConfig.value.dateRange}`,
      generatedAt: "Just now",
      type: reportConfig.value.type,
    };
    recentReports.value.unshift(newReport);
  } catch (error) {
    showError("Error", "Failed to generate report. Please try again.");
  } finally {
    isGenerating.value = false;
  }
};

const viewReport = (reportId) => {
  // Navigate to report detail view
  router.push(`/reports/${reportId}`);
};

const downloadReport = (reportId) => {
  // Find the report to download
  const report = recentReports.value.find((r) => r.id === reportId);
  if (!report) {
    showError("Error", "Report not found.");
    return;
  }

  try {
    // Create report content
    const reportContent = generateReportContent(report);

    // Create and download file
    const blob = new Blob([reportContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${report.title.replace(/\s+/g, "_")}_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    showSuccess(
      "Download Complete",
      "Report has been downloaded successfully."
    );
  } catch (error) {
    showError(
      "Download Failed",
      "Failed to download report. Please try again."
    );
  }
};

const generateReportContent = (report) => {
  // Generate CSV content for the report
  const headers = ["Report Title", "Description", "Type", "Generated At"];
  const data = [
    report.title,
    report.description,
    report.type,
    report.generatedAt,
  ];

  return [headers.join(","), data.join(",")].join("\n");
};

const exportToPDF = () => {
  try {
    // Generate comprehensive report content for PDF export
    const reportContent = generateComprehensiveReportContent();

    // Create and download file (simulating PDF export)
    const blob = new Blob([reportContent], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Audit_Reports_Summary_${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    showSuccess(
      "Export Complete",
      "Reports summary has been exported successfully."
    );
  } catch (error) {
    showError("Export Failed", "Failed to export reports. Please try again.");
  }
};

const generateComprehensiveReportContent = () => {
  const lines = [];

  // Header
  lines.push("AUDIT REPORTS SUMMARY");
  lines.push("Generated: " + new Date().toLocaleString());
  lines.push("=".repeat(50));
  lines.push("");

  // Analytics Summary
  lines.push("ANALYTICS SUMMARY");
  lines.push("Compliance Rate: 87.5%");
  lines.push("Total Violations: 24");
  lines.push("Audits This Month: 156");
  lines.push("Risk Score: Medium");
  lines.push("");

  // Recent Reports
  lines.push("RECENT REPORTS");
  lines.push("-".repeat(30));
  recentReports.value.forEach((report, index) => {
    lines.push(`${index + 1}. ${report.title}`);
    lines.push(`   Description: ${report.description}`);
    lines.push(`   Type: ${report.type}`);
    lines.push(`   Generated: ${report.generatedAt}`);
    lines.push("");
  });

  // Report Configuration
  lines.push("CURRENT REPORT CONFIGURATION");
  lines.push("-".repeat(30));
  lines.push(`Report Type: ${reportConfig.value.type}`);
  lines.push(`Date Range: ${reportConfig.value.dateRange}`);
  lines.push(`Driver Filter: ${reportConfig.value.driverFilter}`);

  return lines.join("\n");
};

const exportAllToCSV = () => {
  try {
    const headers = ["ID", "Title", "Description", "Type", "Generated At"];
    const data = recentReports.value.map((report, index) => [
      index + 1,
      report.title,
      report.description,
      report.type,
      report.generatedAt,
    ]);

    const csvContent = [
      headers.join(","),
      ...data.map((row) => row.join(",")),
    ].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `All_Recent_Reports_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    showSuccess(
      "Export Complete",
      "All recent reports have been exported successfully."
    );
  } catch (error) {
    showError(
      "Export Failed",
      "Failed to export all reports. Please try again."
    );
  }
};

onMounted(() => {
  // Load any necessary data
});
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

/* Stagger animation for report items */
.space-y-4 > div {
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
}

.space-y-4 > div:nth-child(1) {
  animation-delay: 0.1s;
}
.space-y-4 > div:nth-child(2) {
  animation-delay: 0.2s;
}
.space-y-4 > div:nth-child(3) {
  animation-delay: 0.3s;
}
.space-y-4 > div:nth-child(4) {
  animation-delay: 0.4s;
}
.space-y-4 > div:nth-child(5) {
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
a:focus,
input:focus,
select:focus {
  outline: 2px solid #6366f1;
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

/* Card enhancements */
.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
}

/* Button enhancements */
button {
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-1px);
}

/* Form input enhancements */
input,
select {
  transition: all 0.3s ease;
}

input:focus,
select:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

/* Analytics card enhancements */
.analytics-card {
  transition: all 0.3s ease;
}

.analytics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

/* Report item enhancements */
.report-item {
  transition: all 0.3s ease;
}

.report-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.1);
}

/* Loading state enhancements */
.loading {
  transition: opacity 0.3s ease;
}

/* Export button enhancements */
.export-button {
  transition: all 0.3s ease;
}

.export-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}
</style>
