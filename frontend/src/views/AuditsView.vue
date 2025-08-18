<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Audit History</h1>
        <p class="text-gray-600 text-lg">
          View and manage all completed audit records
        </p>
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
      </div>
    </div>

    <!-- Main Content -->
    <div v-if="userStore.isAuthenticated">
      <!-- Loading State -->
      <div v-if="auditStore.isLoading" class="text-center py-12">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"
        ></div>
        <p class="text-muted-foreground">Loading audits...</p>
      </div>

      <!-- Data State -->
      <div v-else>
        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
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
                      d="M5 13l4 4L19 7"
                    ></path>
                  </svg>
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
                <div class="p-2 bg-orange-100 rounded-lg">
                  <svg
                    class="w-6 h-6 text-orange-600"
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
                  <p class="text-sm font-medium text-gray-600">Pending</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ pendingAudits.length }}
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
                  <p class="text-sm font-medium text-gray-600">Violations</p>
                  <p class="text-2xl font-bold text-gray-900">
                    {{ totalViolations }}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Table Summary -->
        <div class="flex justify-between items-center mb-4">
          <div class="text-sm text-gray-700">
            <span v-if="pagination.totalItems > 0">
              Showing {{ startItem }} to {{ endItem }} of
              {{ pagination.totalItems }} audits
            </span>
            <span v-else>No audits found</span>
          </div>
          <div class="text-sm text-gray-500">
            {{ totalPages > 1 ? `${totalPages} pages` : "1 page" }}
          </div>
        </div>

        <!-- Audits Table -->
        <Card data-table="audits">
          <CardContent class="p-0">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Driver
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Type
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Status
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Violations
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Score
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Date
                    </th>
                    <th
                      class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <!-- No data row -->
                  <tr
                    v-if="paginatedAudits.length === 0"
                    class="hover:bg-gray-50"
                  >
                    <td colspan="7" class="px-6 py-12 text-center">
                      <div class="flex flex-col items-center space-y-3">
                        <FileTextIcon class="w-12 h-12 text-gray-400" />
                        <div>
                          <h3 class="text-lg font-medium text-gray-900 mb-1">
                            No audits found
                          </h3>
                          <p class="text-sm text-gray-500">
                            {{
                              pagination.totalItems === 0
                                ? "No audits have been created yet."
                                : "No audits match the current filters."
                            }}
                          </p>
                        </div>
                      </div>
                    </td>
                  </tr>

                  <!-- Data rows -->
                  <tr
                    v-for="audit in paginatedAudits"
                    :key="audit.id"
                    class="hover:bg-gray-50 transition-colors duration-200"
                    :class="{ 'opacity-50': pagination.isLoading }"
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
                      <Badge variant="secondary">{{
                        formatDriverType(audit.driverType)
                      }}</Badge>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <Badge :variant="getStatusVariant(audit.status)">{{
                        formatStatus(audit.status)
                      }}</Badge>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">
                        {{ audit.violations || 0 }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span v-if="audit.summary" class="text-sm text-gray-900"
                        >{{ audit.summary.complianceScore }}%</span
                      >
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
                          >View</Button
                        >
                        <Button
                          variant="ghost"
                          size="sm"
                          @click="() => confirmDelete(audit)"
                          :disabled="deletingAudits.includes(audit.id)"
                          class="text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <svg
                            v-if="deletingAudits.includes(audit.id)"
                            class="w-4 h-4 animate-spin"
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
                          <svg
                            v-else
                            class="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            ></path>
                          </svg>
                          {{
                            deletingAudits.includes(audit.id)
                              ? "Deleting..."
                              : "Delete"
                          }}
                        </Button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <!-- Pagination -->
        <Card v-if="totalPages > 1" class="mt-6">
          <CardContent class="p-4">
            <div
              class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0"
            >
              <!-- Items per page selector -->
              <div class="flex items-center space-x-2">
                <Label for="itemsPerPage" class="text-sm text-gray-700"
                  >Show:</Label
                >
                <Select
                  id="itemsPerPage"
                  v-model="pagination.itemsPerPage"
                  @change="changeItemsPerPage"
                  class="w-20"
                >
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                </Select>
                <span class="text-sm text-gray-700">per page</span>
              </div>

              <!-- Page info -->
              <div class="text-sm text-gray-700 flex items-center space-x-2">
                <span
                  >Showing {{ startItem }} to {{ endItem }} of
                  {{ pagination.totalItems }} results</span
                >
                <div
                  v-if="pagination.isLoading"
                  class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"
                ></div>
              </div>

              <!-- Navigation -->
              <div class="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  @click="previousPage"
                  :disabled="pagination.currentPage === 1"
                  class="px-3 py-1 transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
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
                      d="M15 19l-7-7 7-7"
                    ></path>
                  </svg>
                </Button>

                <!-- Page numbers -->
                <div class="flex items-center space-x-1">
                  <template v-for="page in visiblePages" :key="page">
                    <Button
                      v-if="page !== '...'"
                      :variant="
                        page === pagination.currentPage ? 'default' : 'outline'
                      "
                      size="sm"
                      @click="goToPage(page)"
                      class="px-3 py-1 min-w-[40px] transition-all duration-200 hover:scale-105"
                    >
                      {{ page }}
                    </Button>
                    <span v-else class="px-2 text-gray-500 select-none"
                      >...</span
                    >
                  </template>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  @click="nextPage"
                  :disabled="pagination.currentPage === totalPages"
                  class="px-3 py-1 transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
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
                      d="M9 5l7 7-7 7"
                    ></path>
                  </svg>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Welcome Message for Unauthenticated Users -->
    <div v-else class="text-center py-12">
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
  </div>

  <!-- Delete Confirmation Modal -->
  <div
    v-if="showDeleteModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="cleanupModal"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" @click.stop>
      <!-- Modal Header -->
      <div
        class="flex items-center justify-between p-6 border-b border-gray-200"
      >
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              ></path>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">Delete Audit</h3>
            <p class="text-sm text-gray-500">This action cannot be undone</p>
          </div>
        </div>
        <button
          @click="cancelDeleteAction"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <div class="mb-6">
          <p class="text-gray-700 mb-4">
            Are you sure you want to delete the audit for
            <span class="font-semibold text-gray-900">{{
              auditToDelete?.driverName
            }}</span
            >?
          </p>

          <!-- Audit Details -->
          <div class="bg-gray-50 rounded-lg p-4 space-y-3">
            <h4 class="font-medium text-gray-900 text-sm">Audit Details:</h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-gray-500">Driver:</span>
                <span class="ml-2 font-medium text-gray-900">{{
                  auditToDelete?.driverName
                }}</span>
              </div>
              <div>
                <span class="text-gray-500">Type:</span>
                <span class="ml-2 font-medium text-gray-900">{{
                  formatDriverType(auditToDelete?.driverType)
                }}</span>
              </div>
              <div>
                <span class="text-gray-500">Status:</span>
                <span class="ml-2 font-medium text-gray-900">{{
                  formatStatus(auditToDelete?.status)
                }}</span>
              </div>
              <div>
                <span class="text-gray-500">Date:</span>
                <span class="ml-2 font-medium text-gray-900">{{
                  formatDate(auditToDelete?.createdAt)
                }}</span>
              </div>
              <div>
                <span class="text-gray-500">Files:</span>
                <span class="ml-2 font-medium text-gray-900"
                  >{{ auditToDelete?.files?.length || 0 }} file(s)</span
                >
              </div>
              <div>
                <span class="text-gray-500">Violations:</span>
                <span class="ml-2 font-medium text-gray-900">{{
                  auditToDelete?.violations || 0
                }}</span>
              </div>
            </div>
          </div>

          <!-- Warning -->
          <div class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start space-x-2">
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
              <div class="text-sm text-red-700">
                <p class="font-medium">Warning:</p>
                <ul class="mt-1 space-y-1">
                  <li>• All audit data will be permanently removed</li>
                  <li>• Associated files will be deleted</li>
                  <li>• This will affect your compliance records</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="flex space-x-3">
          <Button variant="outline" @click="cancelDeleteAction" class="flex-1">
            Cancel
          </Button>
          <Button
            variant="destructive"
            @click="confirmDeleteAction"
            class="flex-1"
          >
            Delete Audit
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch, ref } from "vue";
import { useAuditStore } from "../stores/audit";
import { useUserStore } from "../stores/user";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import { FileTextIcon } from "lucide-vue-next";
import { useAlert } from "@/composables/useAlert";

const auditStore = useAuditStore();
const userStore = useUserStore();
const { showAlert } = useAlert();

// Initialize data
const initializeData = async () => {
  if (!userStore.isAuthenticated) return;

  try {
    await auditStore.fetchAudits();
  } catch (error) {
    console.error("Error fetching audits:", error);
  }
};

// Watch for authentication state changes
watch(
  () => userStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) initializeData();
  }
);

// Initialize data when component mounts
initializeData();

// Define filteredAudits FIRST since pagination depends on it
const filteredAudits = computed(() => {
  let audits = auditStore.audits || [];
  if (!Array.isArray(audits)) return [];
  return audits;
});

// Pagination state
const pagination = reactive({
  currentPage: 1,
  itemsPerPage: 10,
  totalItems: 0,
  isLoading: false,
});

// Delete state
const deletingAudits = ref([]);
const showDeleteModal = ref(false);
const auditToDelete = ref(null);

// Pagination computed properties
const totalPages = computed(() =>
  Math.ceil(pagination.totalItems / pagination.itemsPerPage)
);

const paginatedAudits = computed(() => {
  const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
  const endIndex = startIndex + pagination.itemsPerPage;
  return filteredAudits.value.slice(startIndex, endIndex);
});

const startItem = computed(
  () => (pagination.currentPage - 1) * pagination.itemsPerPage + 1
);

const endItem = computed(() =>
  Math.min(
    pagination.currentPage * pagination.itemsPerPage,
    pagination.totalItems
  )
);

// Watch for changes in filtered audits to update pagination
watch(
  filteredAudits,
  (newAudits) => {
    pagination.totalItems = newAudits.length;
    pagination.currentPage = 1;
  },
  { immediate: true }
);

// Pagination methods
const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    pagination.isLoading = true;
    await new Promise((resolve) => setTimeout(resolve, 150));
    pagination.currentPage = page;
    pagination.isLoading = false;
    scrollToTable();
  }
};

const nextPage = async () => {
  if (pagination.currentPage < totalPages.value) {
    pagination.isLoading = true;
    await new Promise((resolve) => setTimeout(resolve, 150));
    pagination.currentPage++;
    pagination.isLoading = false;
    scrollToTable();
  }
};

const previousPage = async () => {
  if (pagination.currentPage > 1) {
    pagination.isLoading = true;
    await new Promise((resolve) => setTimeout(resolve, 150));
    pagination.currentPage--;
    pagination.isLoading = false;
    scrollToTable();
  }
};

const changeItemsPerPage = async (event) => {
  const newSize = parseInt(event.target.value);
  pagination.isLoading = true;
  await new Promise((resolve) => setTimeout(resolve, 150));
  pagination.itemsPerPage = newSize;
  pagination.currentPage = 1;
  pagination.isLoading = false;
};

// Scroll to table
const scrollToTable = () => {
  const tableElement = document.querySelector('[data-table="audits"]');
  if (tableElement) {
    tableElement.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

// Visible pages with ellipsis
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = pagination.currentPage;
  const delta = 2;

  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  const start = Math.max(1, current - delta);
  const end = Math.min(total, current + delta);
  const pages = [];

  if (start > 1) {
    pages.push(1);
    if (start > 2) pages.push("...");
  }

  for (let i = start; i <= end; i++) pages.push(i);

  if (end < total) {
    if (end < total - 1) pages.push("...");
    pages.push(total);
  }

  return pages;
});

// Computed properties for status cards
const completedAudits = computed(() => {
  return filteredAudits.value.filter((audit) => audit.status === "completed");
});

const processingAudits = computed(() => {
  return filteredAudits.value.filter((audit) => audit.status === "processing");
});

const pendingAudits = computed(() => {
  return filteredAudits.value.filter((audit) => audit.status === "pending");
});

const totalViolations = computed(() => {
  return filteredAudits.value.reduce(
    (sum, audit) => sum + (audit.violations || 0),
    0
  );
});

// Utility functions
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

const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

const confirmDelete = async (audit) => {
  // Create a more user-friendly confirmation dialog
  const confirmed = await showDeleteConfirmation(audit);
  if (!confirmed) return;

  try {
    // Add audit to deleting list
    deletingAudits.value.push(audit.id);

    // Call the store method to delete
    await auditStore.deleteAudit(audit.id);

    // Show success message
    showSuccessMessage(`Audit for ${audit.driverName} deleted successfully`);

    // Refresh data to update the table
    await initializeData();
  } catch (error) {
    console.error("Error deleting audit:", error);
    showErrorMessage(
      `Failed to delete audit: ${error.message || "Unknown error"}`
    );
  } finally {
    // Remove from deleting list
    const index = deletingAudits.value.indexOf(audit.id);
    if (index > -1) {
      deletingAudits.value.splice(index, 1);
    }
  }
};

const showDeleteConfirmation = (audit) => {
  return new Promise((resolve) => {
    auditToDelete.value = audit;
    showDeleteModal.value = true;

    // Store the resolve function to call it later
    window.deleteModalResolve = resolve;
  });
};

const showSuccessMessage = (message) => {
  console.log("Showing success message:", message);
  showAlert({
    type: "success",
    title: "Audit Deleted Successfully",
    message: `✅ ${message}\n\nThe audit has been permanently removed from the system.`,
  });
};

const showErrorMessage = (message) => {
  console.log("Showing error message:", message);
  showAlert({
    type: "error",
    title: "Delete Failed",
    message: `❌ ${message}\n\nPlease try again or contact support if the problem persists.`,
  });
};

// Modal methods
const confirmDeleteAction = () => {
  showDeleteModal.value = false;
  auditToDelete.value = null;

  // Resolve the promise with true (confirmed)
  if (window.deleteModalResolve) {
    window.deleteModalResolve(true);
    window.deleteModalResolve = null;
  }
};

const cancelDeleteAction = () => {
  showDeleteModal.value = false;
  auditToDelete.value = null;

  // Resolve the promise with false (cancelled)
  if (window.deleteModalResolve) {
    window.deleteModalResolve(false);
    window.deleteModalResolve = null;
  }
};

// Cleanup function for unexpected modal closures
const cleanupModal = () => {
  if (window.deleteModalResolve) {
    window.deleteModalResolve(false);
    window.deleteModalResolve = null;
  }
  showDeleteModal.value = false;
  auditToDelete.value = null;
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
</script>

<style scoped>
/* Add any custom styles here */
</style>
