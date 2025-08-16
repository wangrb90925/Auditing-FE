<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Audit History</h1>
        <p class="text-gray-600 text-lg">View and manage all audit reports</p>
      </div>
      <div v-if="userStore.isAuthenticated" class="flex space-x-3">
        <Button
          variant="outline"
          @click="exportToCSV"
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
          <span>Export CSV</span>
        </Button>
        <Button
          variant="outline"
          @click="exportToExcel"
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
          <span>Export Excel</span>
        </Button>
      </div>
    </div>

    <!-- Welcome Message for Unauthenticated Users -->
    <div v-if="!userStore.isAuthenticated" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <div
          class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <FileTextIcon class="w-8 h-8 text-gray-400" />
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
      <!-- Loading State -->
      <div v-if="auditStore.isLoading" class="text-center py-12">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"
        ></div>
        <p class="text-muted-foreground">Loading audits...</p>
      </div>

      <!-- No Data State - Show when no audits exist -->
      <div v-else-if="!auditStore.audits || auditStore.audits.length === 0">
        <!-- Filters -->
        <Card class="mb-6">
          <CardHeader>
            <div class="flex items-center space-x-2">
              <FilterIcon class="w-5 h-5 text-gray-500" />
              <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div class="space-y-2">
                <Label for="status" class="text-sm font-medium text-gray-700"
                  >Status</Label
                >
                <Select id="status" v-model="filters.status" class="w-full">
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label
                  for="driverType"
                  class="text-sm font-medium text-gray-700"
                  >Driver Type</Label
                >
                <Select
                  id="driverType"
                  v-model="filters.driverType"
                  class="w-full"
                >
                  <option value="">All Types</option>
                  <option value="long-haul">Long Haul</option>
                  <option value="short-haul">Short Haul</option>
                  <option value="exemption">Exemption</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="dateRange" class="text-sm font-medium text-gray-700"
                  >Date Range</Label
                >
                <Select
                  id="dateRange"
                  v-model="filters.dateRange"
                  class="w-full"
                >
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="quarter">This Quarter</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="search" class="text-sm font-medium text-gray-700"
                  >Search</Label
                >
                <div class="relative">
                  <SearchIcon
                    class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                  />
                  <Input
                    id="search"
                    v-model="filters.search"
                    type="text"
                    placeholder="Search driver name..."
                    class="pl-10 w-full"
                  />
                </div>
              </div>
            </div>
            <div class="flex justify-end mt-6">
              <Button variant="outline" @click="clearFilters" class="mr-2"
                >Clear Filters</Button
              >
              <Button @click="initializeData">Refresh</Button>
            </div>
          </CardContent>
        </Card>

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <FileTextIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Total Audits</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ auditStore.audits?.length || 0 }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                  <CheckIcon class="w-6 h-6 text-green-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Completed</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ completedAudits.length }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-yellow-100 rounded-lg">
                  <ClockIcon class="w-6 h-6 text-yellow-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Processing</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ processingAudits.length }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-red-100 rounded-lg">
                  <AlertTriangleIcon class="w-6 h-6 text-red-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Violations</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ totalViolations }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Audits Table with Empty State -->
        <Card>
          <CardContent class="p-0">
            <div class="overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <UserIcon class="w-4 h-4" />
                        <span>Driver</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <TagIcon class="w-4 h-4" />
                        <span>Type</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <ClockIcon class="w-4 h-4" />
                        <span>Status</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <AlertTriangleIcon class="w-4 h-4" />
                        <span>Violations</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <BarChartIcon class="w-4 h-4" />
                        <span>Compliance Score</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <CalendarIcon class="w-4 h-4" />
                        <span>Date</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <SettingsIcon class="w-4 h-4" />
                        <span>Actions</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <!-- Empty State Row -->
                  <tr>
                    <td colspan="7" class="px-6 py-16 text-center">
                      <div class="max-w-md mx-auto">
                        <div class="relative">
                          <div
                            class="w-24 h-24 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6"
                          >
                            <FileTextIcon class="w-12 h-12 text-blue-600" />
                          </div>
                          <div
                            class="absolute -top-2 -right-2 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
                          >
                            <PlusIcon class="w-4 h-4 text-blue-600" />
                          </div>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900 mb-3">
                          No Audits Found
                        </h3>
                        <p class="text-gray-600 mb-6 leading-relaxed">
                          You haven't created any audits yet. Start by uploading
                          some files to begin your compliance journey.
                        </p>
                        <div
                          class="flex flex-col sm:flex-row gap-3 justify-center"
                        >
                          <Button as-child class="flex items-center space-x-2">
                            <router-link
                              to="/upload"
                              class="flex items-center space-x-2"
                            >
                              <UploadIcon class="w-4 h-4" />
                              <span>Create New Audit</span>
                            </router-link>
                          </Button>
                          <Button
                            variant="outline"
                            @click="initializeData"
                            class="flex items-center space-x-2"
                          >
                            <RefreshCwIcon class="w-4 h-4" />
                            <span>Refresh</span>
                          </Button>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Data Display -->
      <div v-else>
        <!-- Filters -->
        <Card class="mb-6">
          <CardHeader>
            <div class="flex items-center space-x-2">
              <FilterIcon class="w-5 h-5 text-gray-500" />
              <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div class="space-y-2">
                <Label for="status" class="text-sm font-medium text-gray-700"
                  >Status</Label
                >
                <Select id="status" v-model="filters.status" class="w-full">
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label
                  for="driverType"
                  class="text-sm font-medium text-gray-700"
                  >Driver Type</Label
                >
                <Select
                  id="driverType"
                  v-model="filters.driverType"
                  class="w-full"
                >
                  <option value="">All Types</option>
                  <option value="long-haul">Long Haul</option>
                  <option value="short-haul">Short Haul</option>
                  <option value="exemption">Exemption</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="dateRange" class="text-sm font-medium text-gray-700"
                  >Date Range</Label
                >
                <Select
                  id="dateRange"
                  v-model="filters.dateRange"
                  class="w-full"
                >
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="quarter">This Quarter</option>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="search" class="text-sm font-medium text-gray-700"
                  >Search</Label
                >
                <div class="relative">
                  <SearchIcon
                    class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                  />
                  <Input
                    id="search"
                    v-model="filters.search"
                    type="text"
                    placeholder="Search driver name..."
                    class="pl-10 w-full"
                  />
                </div>
              </div>
            </div>
            <div class="flex justify-end mt-6">
              <Button variant="outline" @click="clearFilters" class="mr-2"
                >Clear Filters</Button
              >
              <Button @click="initializeData">Refresh</Button>
            </div>
          </CardContent>
        </Card>

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <FileTextIcon class="w-6 h-6 text-blue-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Total Audits</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ auditStore.audits?.length || 0 }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-green-100 rounded-lg">
                  <CheckIcon class="w-6 h-6 text-green-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Completed</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ completedAudits.length }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-yellow-100 rounded-lg">
                  <ClockIcon class="w-6 h-6 text-yellow-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Processing</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ processingAudits.length }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent class="p-6">
              <div class="flex items-center">
                <div class="p-2 bg-red-100 rounded-lg">
                  <AlertTriangleIcon class="w-6 h-6 text-red-600" />
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600">Violations</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ totalViolations }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Audits Table -->
        <Card>
          <CardContent class="p-0">
            <div class="overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <UserIcon class="w-4 h-4" />
                        <span>Driver</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <TagIcon class="w-4 h-4" />
                        <span>Type</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <ClockIcon class="w-4 h-4" />
                        <span>Status</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <AlertTriangleIcon class="w-4 h-4" />
                        <span>Violations</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <BarChartIcon class="w-4 h-4" />
                        <span>Compliance Score</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <CalendarIcon class="w-4 h-4" />
                        <span>Date</span>
                      </div>
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      <div class="flex items-center space-x-2">
                        <SettingsIcon class="w-4 h-4" />
                        <span>Actions</span>
                      </div>
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
                              width: `${audit.summary.complianceScore}%`,
                            }"
                          ></div>
                        </div>
                        <span class="text-sm text-gray-900">
                          {{ audit.summary.complianceScore }}%
                        </span>
                      </div>
                      <span v-else class="text-sm text-gray-500">N/A</span>
                    </td>
                    <td
                      class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {{ formatDate(audit.createdAt) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          @click="() => $router.push(`/audit/${audit.id}`)"
                        >
                          View
                        </Button>
                        <Button
                          v-if="audit.status === 'completed'"
                          variant="ghost"
                          size="sm"
                          @click="() => downloadReport(audit.id)"
                        >
                          Download
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          @click="() => deleteAudit(audit.id)"
                          class="text-red-600 hover:text-red-800"
                        >
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
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
import { FilterIcon, SearchIcon } from "lucide-vue-next";
import CardHeader from "@/components/ui/card-header.vue";
import {
  FileTextIcon,
  PlusIcon,
  UploadIcon,
  RefreshCwIcon,
} from "lucide-vue-next";
import {
  UserIcon,
  TagIcon,
  ClockIcon,
  AlertTriangleIcon,
  BarChartIcon,
  CalendarIcon,
  SettingsIcon,
  CheckIcon,
} from "lucide-vue-next";

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
    console.log("🔍 Fetching audits from API...");
    // Try to fetch real data from API
    const result = await auditStore.fetchAudits();
    console.log("📊 Fetch result:", result);
    console.log("📋 Audits in store:", auditStore.audits);
  } catch (error) {
    console.error("❌ Error fetching audits:", error);
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

const completedAudits = computed(() => {
  return filteredAudits.value.filter((audit) => audit.status === "completed");
});

const processingAudits = computed(() => {
  return filteredAudits.value.filter((audit) => audit.status === "processing");
});

const totalViolations = computed(() => {
  return filteredAudits.value.reduce(
    (sum, audit) => sum + (audit.violations || 0),
    0
  );
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

const clearFilters = () => {
  filters.status = "";
  filters.driverType = "";
  filters.dateRange = "";
  filters.search = "";
};
</script>
