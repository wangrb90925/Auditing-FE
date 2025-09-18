<template>
  <div class="space-y-6">
    <!-- Enhanced Header with better visual hierarchy -->
    <div class="relative">
      <!-- Background decoration -->
      <div
        class="absolute inset-0 bg-gradient-to-r from-purple-50/50 via-transparent to-blue-50/50 rounded-3xl -z-10"
      ></div>

      <div
        class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6 p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-100/50 shadow-sm"
      >
        <div class="space-y-3">
          <div class="flex items-center space-x-3">
            <div
              class="w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg"
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
            </div>
            <div>
              <h1
                class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
              >
                Audit History
              </h1>
              <p class="text-gray-600 text-lg font-medium">
                View and manage all completed audit records
              </p>
            </div>
          </div>
        </div>

        <div
          v-if="userStore.isAuthenticated"
          class="flex items-center space-x-3"
        >
          <Button
            variant="outline"
            @click="exportToCSV"
            class="export-button flex items-center space-x-2 rounded-xl border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all duration-300 px-6 py-3"
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
            <span class="font-semibold">Export CSV</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-if="userStore.isAuthenticated">
      <!-- Enhanced Loading State -->
      <div v-if="auditStore.isLoading" class="text-center py-16">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <svg
              class="w-10 h-10 text-blue-600 animate-spin"
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
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">Loading Audits...</h3>
        <p class="text-gray-600 leading-relaxed">
          Please wait while we fetch your audit data
        </p>
      </div>

      <!-- Data State -->
      <div v-else>
        <!-- Enhanced Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
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
                    <FileTextIcon class="w-7 h-7 text-white" />
                  </div>
                </div>
                <div class="ml-4">
                  <p
                    class="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1"
                  >
                    Total Audits
                  </p>
                  <p
                    class="text-4xl font-bold text-blue-900 dark:text-blue-100"
                  >
                    {{ auditStore.audits?.length || 0 }}
                  </p>
                  <p class="text-xs text-blue-500/70 mt-1">All time audits</p>
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
                        d="M5 13l4 4L19 7"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p
                    class="text-sm font-medium text-green-600 dark:text-green-400 mb-1"
                  >
                    Completed
                  </p>
                  <p
                    class="text-4xl font-bold text-green-900 dark:text-green-100"
                  >
                    {{ completedAudits.length }}
                  </p>
                  <p class="text-xs text-green-500/70 mt-1">Finished audits</p>
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
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p
                    class="text-sm font-medium text-yellow-600 dark:text-yellow-400 mb-1"
                  >
                    Processing
                  </p>
                  <p
                    class="text-4xl font-bold text-yellow-900 dark:text-yellow-100"
                  >
                    {{ processingAudits.length }}
                  </p>
                  <p class="text-xs text-yellow-500/70 mt-1">In progress</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            class="group bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-950/50 dark:to-orange-900/30 border-orange-200/50 dark:border-orange-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
          >
            <div
              class="absolute inset-0 bg-gradient-to-r from-orange-400/10 to-orange-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            ></div>

            <CardContent class="p-6 relative z-10">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div
                    class="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300"
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
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p
                    class="text-sm font-medium text-orange-600 dark:text-orange-400 mb-1"
                  >
                    Pending
                  </p>
                  <p
                    class="text-4xl font-bold text-orange-900 dark:text-orange-100"
                  >
                    {{ pendingAudits.length }}
                  </p>
                  <p class="text-xs text-orange-500/70 mt-1">Awaiting review</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            class="group bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/50 dark:to-red-900/30 border-red-200/50 dark:border-red-800/50 hover:shadow-xl hover:scale-105 transition-all duration-500 cursor-pointer overflow-hidden relative"
          >
            <div
              class="absolute inset-0 bg-gradient-to-br from-red-400/10 to-red-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
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
                        d="M12 9v2m0 4h.01m-6.938 4h16a2 2 0 002-2V5a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-4">
                  <p
                    class="text-sm font-medium text-red-600 dark:text-red-400 mb-1"
                  >
                    Violations
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

        <!-- Enhanced Table Summary -->
        <div
          class="flex justify-between items-center mb-6 p-4 bg-gradient-to-r from-gray-50 to-gray-100/50 rounded-xl border border-gray-200/50"
        >
          <div class="flex items-center space-x-3">
            <div
              class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-4 h-4 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                ></path>
              </svg>
            </div>
            <div class="text-sm font-medium text-gray-700">
              <span v-if="pagination.totalItems > 0">
                Showing
                <span class="font-semibold text-blue-600">{{ startItem }}</span>
                to
                <span class="font-semibold text-blue-600">{{ endItem }}</span>
                of
                <span class="font-semibold text-blue-600">{{
                  pagination.totalItems
                }}</span>
                audits
              </span>
              <span v-else class="text-gray-500">No audits found</span>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div class="text-sm font-medium text-gray-600">
              {{ totalPages > 1 ? `${totalPages} pages` : "1 page" }}
            </div>
          </div>
        </div>

        <!-- Enhanced Audits Table -->
        <Card
          class="bg-white/80 backdrop-blur-sm border-gray-100/50 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden"
          data-table="audits"
        >
          <CardContent class="p-0">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
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
                      Violations
                    </th>
                    <th
                      class="px-8 py-5 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                    >
                      Score
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
                <tbody class="bg-white divide-y divide-gray-200">
                  <!-- Enhanced No data row -->
                  <tr
                    v-if="paginatedAudits.length === 0"
                    class="hover:bg-gray-50"
                  >
                    <td colspan="7" class="px-8 py-16 text-center">
                      <div class="flex flex-col items-center space-y-4">
                        <div class="relative">
                          <div
                            class="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center shadow-lg"
                          >
                            <FileTextIcon class="w-10 h-10 text-gray-400" />
                          </div>
                          <div
                            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full animate-pulse"
                          ></div>
                        </div>
                        <div>
                          <h3 class="text-xl font-bold text-gray-900 mb-2">
                            No audits found
                          </h3>
                          <p class="text-gray-600 leading-relaxed">
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

                  <!-- Enhanced Data rows -->
                  <tr
                    v-for="(audit, index) in paginatedAudits"
                    :key="audit.id"
                    class="hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 transition-all duration-300 group"
                    :class="{ 'opacity-50': pagination.isLoading }"
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
                          <div class="text-sm text-gray-500">
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
                      <div class="flex items-center">
                        <div
                          class="w-12 h-8 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg flex items-center justify-center mr-2"
                        >
                          <span class="text-sm font-bold text-gray-700">
                            {{ formatScore(audit) }}%
                          </span>
                        </div>
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
                          @click="() => $router.push(`/audit/${audit.id}`)"
                          class="rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-all duration-300 group-hover:scale-105"
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
                          variant="ghost"
                          size="sm"
                          @click="() => confirmDelete(audit)"
                          :disabled="deletingAudits.includes(audit.id)"
                          class="text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-all duration-300 group-hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
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
                          <span v-else>Delete</span>
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

const formatScore = (audit) => {
  const raw = audit?.summary?.complianceScore;
  if (typeof raw === "number") return raw;
  const v = audit?.violations ?? 0;
  return v > 0 ? 0 : 100;
};

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

/* Table row enhancements */
tbody tr {
  transition: all 0.3s ease;
}

tbody tr:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

/* Badge enhancements */
.badge {
  transition: all 0.3s ease;
}

.badge:hover {
  transform: scale(1.05);
}

/* Loading state enhancements */
.opacity-50 {
  transition: opacity 0.3s ease;
}

/* Pagination enhancements */
.pagination-item {
  transition: all 0.3s ease;
}

.pagination-item:hover {
  transform: scale(1.1);
}

/* Export button enhancements */
.export-button {
  transition: all 0.3s ease;
}

.export-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}
</style>
