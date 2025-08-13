<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit History</h1>
        <p class="text-gray-600">View and manage all audit reports</p>
      </div>
      <div v-if="userStore.isAuthenticated" class="flex space-x-3">
        <Button variant="outline" @click="exportToCSV">
          <svg
            class="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export CSV
        </Button>
        <Button variant="outline" @click="exportToExcel">
          <svg
            class="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export Excel
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
          Welcome to Audit History
        </h3>
        <p class="text-sm text-gray-500 mb-4">
          Please sign in to view and manage your audit reports
        </p>
        <Button as-child>
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>

    <!-- Main Content for Authenticated Users -->
    <div v-else>
      <!-- Filters -->
      <Card>
        <CardContent class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label for="status">Status</Label>
              <Select id="status" v-model="filters.status">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </Select>
            </div>
            <div>
              <Label for="driverType">Driver Type</Label>
              <Select id="driverType" v-model="filters.driverType">
                <option value="">All Types</option>
                <option value="long-haul">Long Haul</option>
                <option value="short-haul">Short Haul</option>
                <option value="exemption">Exemption</option>
              </Select>
            </div>
            <div>
              <Label for="dateRange">Date Range</Label>
              <Select id="dateRange" v-model="filters.dateRange">
                <option value="">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
              </Select>
            </div>
            <div>
              <Label for="search">Search</Label>
              <Input
                id="search"
                v-model="filters.search"
                type="text"
                placeholder="Search driver name..."
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Audits Table -->
      <Card>
        <CardContent class="p-0">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Driver
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Type
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Status
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Violations
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Compliance Score
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Date
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
                  v-for="audit in filteredAudits"
                  :key="audit.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">
                      {{ audit.driverName }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ audit.files?.length || 0 }} files
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <Badge variant="secondary">
                      {{ formatDriverType(audit.driverType) }}
                    </Badge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <Badge :variant="getStatusVariant(audit.status)">
                      {{ formatStatus(audit.status) }}
                    </Badge>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">
                      {{ audit.violations || 0 }}
                    </div>
                    <div
                      v-if="audit.violations > 0"
                      class="text-xs text-danger-600"
                    >
                      {{ audit.violationsList?.length || 0 }} violations found
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div v-if="audit.summary" class="flex items-center">
                      <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          :class="
                            getComplianceColor(audit.summary.complianceScore)
                          "
                          class="h-2 rounded-full"
                          :style="{
                            width: audit.summary.complianceScore + '%',
                          }"
                        ></div>
                      </div>
                      <span class="text-sm text-gray-900"
                        >{{ audit.summary.complianceScore }}%</span
                      >
                    </div>
                    <div v-else class="text-sm text-gray-500">-</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(audit.createdAt) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                      <Button variant="ghost" size="sm" as-child>
                        <router-link :to="`/audit/${audit.id}`"
                          >View</router-link
                        >
                      </Button>
                      <Button
                        v-if="audit.status === 'completed'"
                        variant="ghost"
                        size="sm"
                        @click="downloadReport(audit.id)"
                      >
                        Download
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        @click="deleteAudit(audit.id)"
                        class="text-danger-600 hover:text-danger-800"
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-if="filteredAudits.length === 0" class="text-center py-12">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">
              No audits found
            </h3>
            <p class="mt-1 text-sm text-gray-500">
              Get started by uploading some files for audit.
            </p>
            <div class="mt-6">
              <Button as-child>
                <router-link to="/upload">Upload Files</router-link>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from "vue";
import { useAuditStore } from "../stores/audit";
import { useUserStore } from "../stores/user";
import Button from "@/components/ui/button.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import Card from "@/components/ui/card.vue";
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
  SearchIcon,
  FilterIcon,
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

const filters = reactive({
  status: "",
  driverType: "",
  dateRange: "",
  search: "",
});

const filteredAudits = computed(() => {
  let audits = auditStore.audits || [];

  // Ensure audits is an array
  if (!Array.isArray(audits)) {
    return [];
  }

  // Filter by status
  if (filters.status) {
    audits = audits.filter((audit) => audit.status === filters.status);
  }

  // Filter by driver type
  if (filters.driverType) {
    audits = audits.filter((audit) => audit.driverType === filters.driverType);
  }

  // Filter by search
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase();
    audits = audits.filter((audit) =>
      audit.driverName.toLowerCase().includes(searchTerm)
    );
  }

  // Filter by date range
  if (filters.dateRange) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    audits = audits.filter((audit) => {
      const auditDate = new Date(audit.createdAt);

      switch (filters.dateRange) {
        case "today": {
          return auditDate >= today;
        }
        case "week": {
          const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
          return auditDate >= weekAgo;
        }
        case "month": {
          const monthAgo = new Date(
            today.getFullYear(),
            today.getMonth() - 1,
            today.getDate()
          );
          return auditDate >= monthAgo;
        }
        case "quarter": {
          const quarterAgo = new Date(
            today.getFullYear(),
            today.getMonth() - 3,
            today.getDate()
          );
          return auditDate >= quarterAgo;
        }
        default: {
          return true;
        }
      }
    });
  }

  return audits;
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
    pending: "Pending",
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
  return variants[status] || "secondary";
};

const getComplianceColor = (score) => {
  if (score >= 80) return "bg-success-500";
  if (score >= 60) return "bg-warning-500";
  return "bg-danger-500";
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const deleteAudit = (auditId) => {
  if (confirm("Are you sure you want to delete this audit?")) {
    auditStore.deleteAudit(auditId);
  }
};

const downloadReport = (auditId) => {
  const audit = auditStore.getAuditById(auditId);
  if (!audit) return;

  // Create CSV content
  const csvContent = [
    [
      "Driver Name",
      "Driver Type",
      "Status",
      "Violations",
      "Compliance Score",
      "Date",
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
  a.download = `audit-${auditId}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

const exportToCSV = () => {
  const csvContent = [
    [
      "Driver Name",
      "Driver Type",
      "Status",
      "Violations",
      "Compliance Score",
      "Date",
    ],
    ...filteredAudits.value.map((audit) => [
      audit.driverName,
      formatDriverType(audit.driverType),
      formatStatus(audit.status),
      audit.violations || 0,
      audit.summary?.complianceScore || "N/A",
      formatDate(audit.createdAt),
    ]),
  ]
    .map((row) => row.join(","))
    .join("\n");

  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "audits-export.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

const exportToExcel = () => {
  // For now, just call CSV export
  // In a real implementation, you would use a library like xlsx
  exportToCSV();
};
</script>
