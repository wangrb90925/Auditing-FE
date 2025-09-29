<template>
  <div class="space-y-8">
    <!-- Enhanced Header with better visual hierarchy -->
    <div class="relative">
      <!-- Background decoration -->
      <div
        class="absolute inset-0 bg-gradient-to-r from-green-50/50 via-transparent to-blue-50/50 rounded-3xl -z-10"
      ></div>

      <div
        class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6 p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-100/50 shadow-sm"
      >
        <div class="space-y-3">
          <div class="flex items-center space-x-3">
            <div
              class="w-12 h-12 bg-gradient-to-br from-green-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <UploadIcon class="w-7 h-7 text-white" />
            </div>
            <div>
              <h1
                class="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
              >
                Upload HOS Audit Files
              </h1>
              <p class="text-gray-600 text-lg font-medium">
                Upload ELD logs, fuel receipts, and BOLs for FMCSA
                Hours-of-Service compliance auditing
              </p>
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-3">
          <div class="text-right">
            <div class="text-sm text-gray-500">Current User</div>
            <div class="font-semibold text-gray-900">
              {{ userStore.user?.first_name }} {{ userStore.user?.last_name }}
            </div>
            <div class="text-xs text-gray-500 capitalize">
              {{ userStore.user?.role }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="canUpload" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Enhanced Upload Form -->
      <Card
        class="bg-white/80 backdrop-blur-sm border-gray-100/50 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden"
      >
        <CardHeader
          class="bg-gradient-to-r from-green-50 to-green-100/50 border-b border-green-200/50"
        >
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center"
            >
              <DocumentIcon class="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">Upload Documents</h2>
              <p class="text-gray-600 font-medium">
                Upload driver logs and supporting documentation
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent class="p-8">
          <form @submit.prevent="handleSubmit" class="space-y-8">
            <!-- Driver Information -->
            <div class="space-y-4">
              <Label
                for="driverName"
                class="text-sm font-semibold text-gray-700"
              >
                Driver Name
              </Label>
              <Input
                id="driverName"
                v-model="formData.driverName"
                type="text"
                required
                placeholder="Enter driver name"
                class="h-12 text-lg border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-xl transition-all duration-300"
              />
            </div>

            <!-- Driver Type Selection -->
            <div class="space-y-4">
              <Label
                for="driverType"
                class="text-sm font-semibold text-gray-700"
              >
                Driver Type
              </Label>
              <Select
                id="driverType"
                v-model="formData.driverType"
                required
                class="h-12 text-lg border-gray-300 focus:border-green-500 focus:ring-green-500 rounded-xl transition-all duration-300"
              >
                <option value="">Select driver type</option>
                <option value="long-haul">
                  Long Haul (Beyond 150 air miles)
                </option>
                <option value="short-haul">
                  Short Haul (Within 150 air miles)
                </option>
                <option value="exemption">
                  Exemption (Special certificates)
                </option>
              </Select>
            </div>

            <!-- Enhanced File Upload -->
            <div class="space-y-4">
              <Label class="text-sm font-semibold text-gray-700">
                Upload Files
              </Label>
              <div
                @drop.prevent="handleDrop"
                @dragover.prevent
                @dragenter.prevent
                class="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center hover:border-green-400 hover:bg-green-50/50 transition-all duration-500 mt-1 group cursor-pointer"
                :class="{ 'border-green-400 bg-green-50/50': isDragOver }"
              >
                <div class="relative">
                  <div
                    class="w-20 h-20 bg-gradient-to-br from-green-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300"
                  >
                    <UploadIcon class="h-10 w-10 text-green-600" />
                  </div>
                  <div
                    class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-green-500 to-blue-500 rounded-full animate-pulse"
                  ></div>
                </div>

                <div class="space-y-4">
                  <Button
                    type="button"
                    variant="outline"
                    @click="$refs.fileInput.click()"
                    class="rounded-xl border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400 px-8 py-3 text-lg font-semibold transition-all duration-300 hover:scale-105"
                  >
                    Select Files
                  </Button>
                  <div class="space-y-2">
                    <p class="text-gray-600 font-medium">
                      Drag and drop or click to upload ELD logs, fuel receipts,
                      and BOLs
                    </p>
                    <p class="text-sm text-gray-500">
                      Supported: PDF, JPEG, PNG, Excel files
                    </p>
                  </div>
                </div>

                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls"
                  @change="handleFileSelect"
                  class="hidden"
                />
              </div>
            </div>

            <!-- Enhanced File List -->
            <div v-if="selectedFiles.length > 0" class="space-y-4">
              <Label class="text-sm font-semibold text-gray-700">
                Selected Files ({{ selectedFiles.length }})
              </Label>
              <div class="space-y-3">
                <div
                  v-for="(file, index) in selectedFiles"
                  :key="index"
                  class="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100/50 rounded-xl border border-gray-200/50 hover:shadow-md transition-all duration-300 group"
                >
                  <div class="flex items-center">
                    <div
                      class="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300"
                    >
                      <DocumentIcon class="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <span class="text-sm font-semibold text-gray-900">{{
                        file.name
                      }}</span>
                      <span
                        class="ml-3 text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full"
                        >{{ formatFileSize(file.size) }}</span
                      >
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    @click="removeFile(index)"
                    class="text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg p-2 transition-all duration-300 hover:scale-110"
                  >
                    <XIcon class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- Enhanced Submit Button -->
            <div class="flex justify-end pt-6">
              <Button
                type="submit"
                :disabled="isSubmitting || selectedFiles.length === 0"
                size="lg"
                class="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 shadow-xl hover:shadow-2xl rounded-2xl px-10 py-4 text-lg font-semibold transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshIcon
                  v-if="isSubmitting"
                  class="animate-spin -ml-1 mr-3 h-6 w-6"
                />
                {{
                  isSubmitting ? "Processing HOS Audit..." : "Start FMCSA Audit"
                }}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- Enhanced Instructions -->
      <div class="space-y-6">
        <Card
          class="bg-gradient-to-br from-blue-50/80 to-blue-100/60 border-blue-200/50 hover:shadow-xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
        >
          <!-- Animated background elements -->
          <div
            class="absolute top-0 right-0 w-32 h-32 bg-blue-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-24 h-24 bg-blue-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
          ></div>

          <CardHeader class="relative z-10">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center"
              >
                <DocumentIcon class="w-5 h-5 text-white" />
              </div>
              <h3
                class="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300"
              >
                Required Documents
              </h3>
            </div>
          </CardHeader>

          <CardContent class="relative z-10">
            <div class="space-y-6">
              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <DocumentIcon class="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-2">
                    ELD Driver Logs (PDF)
                  </h4>
                  <p class="text-gray-600 leading-relaxed">
                    Electronic logging device records for the audit period
                  </p>
                </div>
              </div>

              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-green-100 to-green-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <DocumentIcon class="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-2">
                    Fuel Receipts (JPEG/PDF)
                  </h4>
                  <p class="text-gray-600 leading-relaxed">
                    Fuel purchase receipts to verify duty status accuracy
                  </p>
                </div>
              </div>

              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <DocumentIcon class="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-2">
                    Bills of Lading (JPEG/PDF)
                  </h4>
                  <p class="text-gray-600 leading-relaxed">
                    Shipping documents to verify cargo and route information
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="bg-gradient-to-br from-green-50/80 to-green-100/60 border-green-200/50 hover:shadow-xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
        >
          <div
            class="absolute top-0 right-0 w-32 h-32 bg-green-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-24 h-24 bg-green-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
          ></div>

          <CardHeader class="relative z-10">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center"
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
              </div>
              <h3
                class="text-xl font-bold text-gray-900 group-hover:text-green-600 transition-colors duration-300"
              >
                FMCSA Compliance Rules
              </h3>
            </div>
          </CardHeader>

          <CardContent class="relative z-10">
            <div class="space-y-6">
              <div>
                <h4 class="font-semibold text-gray-900 mb-3 text-lg">
                  Hours-of-Service (HOS) Violations
                </h4>
                <ul class="text-gray-600 space-y-2">
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-red-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Driving beyond 14 consecutive hours after 10 consecutive
                    hours off duty
                  </li>
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-red-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Exceeding 60/70 hour limits in 7/8 day windows
                  </li>
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-red-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    No record of duty status for logged time
                  </li>
                </ul>
              </div>

              <div>
                <h4 class="font-semibold text-gray-900 mb-3 text-lg">
                  Other Violations
                </h4>
                <ul class="text-gray-600 space-y-2">
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Log falsification and form/manner violations
                  </li>
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Driving while marked off duty
                  </li>
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Fueling while off duty
                  </li>
                  <li class="flex items-start">
                    <span
                      class="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"
                    ></span>
                    Implausible behavior (geographic inconsistencies)
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          class="bg-gradient-to-br from-amber-50/80 to-amber-100/60 border-amber-200/50 hover:shadow-xl hover:scale-105 transition-all duration-500 group cursor-pointer overflow-hidden relative"
        >
          <div
            class="absolute top-0 right-0 w-32 h-32 bg-amber-200/20 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform duration-700"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-24 h-24 bg-amber-300/20 rounded-full translate-y-12 -translate-x-12 group-hover:scale-150 transition-transform duration-700"
          ></div>

          <CardHeader class="relative z-10">
            <div class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center"
              >
                <InfoIcon class="w-5 h-5 text-white" />
              </div>
              <h3
                class="text-xl font-bold text-gray-900 group-hover:text-amber-600 transition-colors duration-300"
              >
                Processing Information
              </h3>
            </div>
          </CardHeader>

          <CardContent class="relative z-10">
            <div class="space-y-6">
              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <svg
                    class="w-5 h-5 text-amber-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    ></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-900 font-semibold mb-1">
                    AI-Powered Analysis
                  </p>
                  <p class="text-gray-600 leading-relaxed">
                    Documents are processed using advanced AI for FMCSA
                    compliance detection
                  </p>
                </div>
              </div>

              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <svg
                    class="w-5 h-5 text-amber-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    ></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-900 font-semibold mb-1">
                    Driver Type Specific
                  </p>
                  <p class="text-gray-600 leading-relaxed">
                    Audit logic adapts based on driver classification and
                    exemptions
                  </p>
                </div>
              </div>

              <div class="flex items-start group/item">
                <div
                  class="w-10 h-10 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mr-4 mt-0.5 group-hover/item:scale-110 transition-transform duration-300"
                >
                  <svg
                    class="w-5 h-5 text-amber-600"
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
                </div>
                <div>
                  <p class="text-gray-900 font-semibold mb-1">
                    Exportable Reports
                  </p>
                  <p class="text-gray-600 leading-relaxed">
                    Detailed CSV/Excel reports with violation analysis and
                    compliance scores
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Enhanced Loading State -->
    <div v-else-if="!userStore.isInitialized" class="text-center py-16">
      <div class="max-w-md mx-auto">
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
        <h3 class="text-2xl font-bold text-gray-900 mb-3">Loading...</h3>
        <p class="text-gray-600 leading-relaxed">
          Please wait while we verify your permissions.
        </p>
      </div>
    </div>

    <!-- Enhanced Not Authenticated Message -->
    <div v-else-if="!userStore.isAuthenticated" class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <svg
              class="w-10 h-10 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 002 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              ></path>
            </svg>
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">Please Sign In</h3>
        <p class="text-gray-600 mb-6 leading-relaxed">
          You need to sign in to access the upload functionality.
        </p>
        <Button
          as-child
          class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg rounded-xl px-8 py-3"
        >
          <router-link to="/login">Sign In</router-link>
        </Button>
      </div>
    </div>

    <!-- Enhanced Access Denied Message -->
    <div v-else class="text-center py-16">
      <div class="max-w-md mx-auto">
        <div class="relative">
          <div
            class="w-20 h-20 bg-gradient-to-br from-red-100 to-red-200 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <svg
              class="w-10 h-10 text-red-600"
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
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-red-500 to-red-600 rounded-full animate-pulse"
          ></div>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">Access Denied</h3>
        <p class="text-gray-600 mb-6 leading-relaxed">
          You don't have permission to upload files. Only auditors and
          administrators can perform this action.
        </p>
        <Button
          as-child
          class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg rounded-xl px-8 py-3"
        >
          <router-link to="/dashboard">Back to Dashboard</router-link>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { useAuditStore } from "../stores/audit";
import { useAlert } from "../composables/useAlert";
import Button from "@/components/ui/button.vue";
import Input from "@/components/ui/input.vue";
import Label from "@/components/ui/label.vue";
import Select from "@/components/ui/select.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import {
  UploadIcon,
  DocumentIcon,
  XIcon,
  RefreshIcon,
  InfoIcon,
} from "@/assets/icons";

const router = useRouter();
const userStore = useUserStore();
const auditStore = useAuditStore();
const { showError, showSuccess } = useAlert();

// Ensure userStore is available
if (!userStore) {
  console.error("userStore is not available");
}

// Safe computed property to prevent undefined errors
const canUpload = computed(() => {
  try {
    // Check if userStore and its properties exist
    if (!userStore || !userStore.isInitialized) {
      return false;
    }

    // Check if user is authenticated
    if (!userStore.isAuthenticated) {
      return false;
    }

    // Check if user has upload permissions
    if (userStore.canUpload === undefined) {
      // Fallback to role-based check
      return userStore.isAdmin || userStore.isAuditor;
    }

    return userStore.canUpload;
  } catch (error) {
    console.warn("Error accessing userStore properties:", error);
    return false;
  }
});

// Ensure user store is initialized
onMounted(async () => {
  if (!userStore.isInitialized) {
    await userStore.initializeAuth();
  }
});

const formData = reactive({
  driverName: "",
  driverType: "",
});

const selectedFiles = ref([]);
const isDragOver = ref(false);
const isSubmitting = ref(false);

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  addFiles(files);
};

const handleDrop = (event) => {
  isDragOver.value = false;
  const files = Array.from(event.dataTransfer.files);
  addFiles(files);
};

const addFiles = (files) => {
  const validTypes = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
  ];

  files.forEach((file) => {
    if (validTypes.includes(file.type)) {
      selectedFiles.value.push(file);
    }
  });
};

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1);
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const handleSubmit = async () => {
  if (selectedFiles.value.length === 0) {
    showError("Validation Error", "Please select at least one file to upload");
    return;
  }

  if (!formData.driverName.trim()) {
    showError("Validation Error", "Please enter a driver name");
    return;
  }

  if (!formData.driverType) {
    showError("Validation Error", "Please select a driver type");
    return;
  }

  isSubmitting.value = true;

  try {
    // Step 1: Create audit
    const auditData = {
      driverName: formData.driverName.trim(),
      driverType: formData.driverType,
    };

    console.log("Creating audit with data:", auditData);
    const result = await auditStore.createAudit(auditData);

    if (!result.success) {
      throw new Error(result.error || "Failed to create audit");
    }

    const newAudit = result.audit;
    console.log("Audit created successfully:", newAudit);

    if (!newAudit || !newAudit.id) {
      throw new Error("Invalid audit response: missing audit ID");
    }

    // Step 2: Upload files
    console.log("Uploading files for audit:", newAudit.id);
    const uploadResult = await auditStore.uploadFiles(
      newAudit.id,
      selectedFiles.value,
    );

    if (!uploadResult.success) {
      throw new Error(uploadResult.error || "Failed to upload files");
    }

    console.log("Files uploaded successfully:", uploadResult.files);

    // Step 3: Process audit with AI engine
    console.log("Processing audit with AI engine:", newAudit.id);
    const processResult = await auditStore.processAudit(newAudit.id);

    if (!processResult.success) {
      throw new Error(processResult.error || "Failed to process audit");
    }

    console.log("Audit processed successfully:", processResult.audit);

    // Step 4: Show success message and redirect
    const rawScore = processResult.audit?.summary?.complianceScore;
    const computedScore =
      typeof rawScore === "number"
        ? rawScore
        : (processResult.audit?.violations || 0) > 0
          ? 0
          : 100;

    showSuccess(
      "Audit Completed Successfully",
      `Driver: ${formData.driverName}\nType: ${formData.driverType}\nCompliance Score: ${computedScore}%\nViolations Found: ${processResult.audit.violations || 0}`,
      8000,
    );

    // Redirect to audit detail view
    router.push(`/audit/${newAudit.id}`);
  } catch (error) {
    console.error("Error in audit workflow:", error);

    // Show user-friendly error message
    let errorMessage = "An error occurred during the audit process.";

    if (error.message.includes("Validation error")) {
      errorMessage = "Please check your input data and try again.";
    } else if (error.message.includes("Unauthorized")) {
      errorMessage = "Please log in again to continue.";
    } else if (error.message.includes("No files uploaded")) {
      errorMessage = "Please upload at least one file for processing.";
    } else {
      errorMessage = `Error: ${error.message}`;
    }

    showError("Error", errorMessage);
  } finally {
    isSubmitting.value = false;
  }
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
  outline: 2px solid #10b981;
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

/* File upload area enhancements */
.border-dashed {
  border-style: dashed;
}

/* Enhanced form styling */
input,
select {
  transition: all 0.3s ease;
}

input:focus,
select:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

/* File list item animations */
.file-item-enter-active,
.file-item-leave-active {
  transition: all 0.3s ease;
}

.file-item-enter-from,
.file-item-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
