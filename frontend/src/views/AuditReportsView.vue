<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Audit Reports</h1>
        <p class="text-gray-600 text-lg">
          Generate comprehensive audit reports and analytics
        </p>
      </div>
      <div v-if="userStore.isAuthenticated" class="flex space-x-3">
        <Button
          variant="outline"
          @click="generateReport"
          class="flex items-center space-x-2"
        >
          <DocumentIcon class="w-4 h-4" />
          <span>Generate Report</span>
        </Button>
        <Button
          variant="outline"
          @click="exportToPDF"
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
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <span>Export Summary</span>
        </Button>
        <Button
          variant="outline"
          @click="exportAllToCSV"
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
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <span>Export CSV</span>
        </Button>
      </div>
    </div>

    <!-- Welcome Message for Unauthenticated Users -->
    <div v-if="!userStore.isAuthenticated" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <div
          class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <DocumentIcon class="w-8 h-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Welcome to Audit Reports
        </h3>
        <p class="text-sm text-gray-500 mb-4">
          Please sign in to generate and view audit reports
        </p>
        <Button as-child>
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>

    <!-- Main Content for Authenticated Users -->
    <div v-else>
      <!-- Report Generation Section -->
      <Card class="mb-6">
        <CardHeader>
          <div class="flex items-center space-x-2">
            <svg
              class="w-5 h-5 text-gray-500"
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
            <h3 class="text-lg font-semibold text-gray-900">
              Generate New Report
            </h3>
          </div>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="space-y-2">
              <Label for="reportType" class="text-sm font-medium text-gray-700"
                >Report Type</Label
              >
              <Select
                id="reportType"
                v-model="reportConfig.type"
                class="w-full"
              >
                <option value="compliance">Compliance Summary</option>
                <option value="violations">Violations Analysis</option>
                <option value="trends">Trends Report</option>
                <option value="comprehensive">Comprehensive Audit</option>
              </Select>
            </div>
            <div class="space-y-2">
              <Label for="dateRange" class="text-sm font-medium text-gray-700"
                >Date Range</Label
              >
              <Select
                id="dateRange"
                v-model="reportConfig.dateRange"
                class="w-full"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="1y">Last Year</option>
                <option value="custom">Custom Range</option>
              </Select>
            </div>
            <div class="space-y-2">
              <Label
                for="driverFilter"
                class="text-sm font-medium text-gray-700"
                >Driver Filter</Label
              >
              <Select
                id="driverFilter"
                v-model="reportConfig.driverFilter"
                class="w-full"
              >
                <option value="all">All Drivers</option>
                <option value="specific">Specific Driver</option>
                <option value="team">Team Drivers</option>
              </Select>
            </div>
          </div>
          <div class="mt-6 flex justify-end">
            <Button @click="generateReport" :disabled="isGenerating">
              <svg
                v-if="isGenerating"
                class="animate-spin -ml-1 mr-3 h-4 w-4 text-white"
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

      <!-- Analytics Dashboard -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent class="p-6">
            <div class="flex items-center space-x-2">
              <div
                class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-4 h-4 text-green-600"
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
              <div>
                <p class="text-sm font-medium text-gray-600">Compliance Rate</p>
                <p class="text-2xl font-bold text-gray-900">87.5%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center space-x-2">
              <div
                class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-4 h-4 text-red-600"
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
              <div>
                <p class="text-sm font-medium text-gray-600">
                  Total Violations
                </p>
                <p class="text-2xl font-bold text-gray-900">24</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center space-x-2">
              <div
                class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-4 h-4 text-blue-600"
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
                <p class="text-sm font-medium text-gray-600">
                  Audits This Month
                </p>
                <p class="text-2xl font-bold text-gray-900">156</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent class="p-6">
            <div class="flex items-center space-x-2">
              <div
                class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center"
              >
                <svg
                  class="w-4 h-4 text-yellow-600"
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
                <p class="text-sm font-medium text-gray-600">Risk Score</p>
                <p class="text-2xl font-bold text-gray-900">Medium</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Recent Reports -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <svg
                class="w-5 h-5 text-gray-500"
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
              <h3 class="text-lg font-semibold text-gray-900">
                Recent Reports
              </h3>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div
              v-for="report in recentReports"
              :key="report.id"
              class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div class="flex items-center space-x-4">
                <div
                  class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center"
                >
                  <DocumentIcon class="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 class="font-medium text-gray-900">{{ report.title }}</h4>
                  <p class="text-sm text-gray-500">{{ report.description }}</p>
                  <p class="text-xs text-gray-400">
                    Generated {{ report.generatedAt }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  @click="viewReport(report.id)"
                >
                  View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  @click="downloadReport(report.id)"
                >
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
/* Add any custom styles here */
</style>
