<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-foreground mb-2">
          FMCSA Audit Results
        </h1>
        <p class="text-muted-foreground text-lg">
          AI-powered compliance analysis for {{ audit?.driverName }}
        </p>
      </div>
      <div class="flex space-x-3">
        <Button variant="outline" @click="downloadReport">
          <DownloadIcon class="w-4 h-4 mr-2" />
          Download Report
        </Button>
        <Button variant="outline" @click="downloadFiles">
          <DownloadIcon class="w-4 h-4 mr-2" />
          Download Files
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"
      ></div>
      <p class="text-muted-foreground">Analyzing compliance data...</p>
    </div>

    <!-- Audit Results -->
    <div v-else-if="audit" class="space-y-6">
      <!-- Compliance Score Card -->
      <Card
        class="bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200/50"
      >
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-blue-900">Compliance Score</h2>
              <p class="text-blue-600">Overall FMCSA compliance rating</p>
            </div>
            <div class="text-center">
              <div class="relative w-24 h-24">
                <svg
                  class="w-24 h-24 transform -rotate-90"
                  viewBox="0 0 100 100"
                >
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="currentColor"
                    stroke-width="8"
                    fill="transparent"
                    class="text-blue-200"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="currentColor"
                    stroke-width="8"
                    fill="transparent"
                    :stroke-dasharray="circumference"
                    :stroke-dashoffset="strokeDashoffset"
                    class="text-blue-600 transition-all duration-1000"
                  />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-2xl font-bold text-blue-900">
                    {{ audit.summary?.complianceScore || 0 }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Violations Summary -->
      <Card>
        <CardHeader>
          <h2 class="text-xl font-bold text-foreground">Violations Found</h2>
          <p class="text-sm text-muted-foreground">
            {{ audit.violations || 0 }} violations detected in
            {{ audit.files?.length || 0 }} files
          </p>
        </CardHeader>
        <CardContent>
          <div
            v-if="audit.violationsList && audit.violationsList.length > 0"
            class="space-y-4"
          >
            <div
              v-for="(violation, index) in audit.violationsList"
              :key="index"
              class="p-4 border rounded-lg"
              :class="getViolationBorderClass(violation.severity)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-2 mb-2">
                    <Badge :variant="getViolationVariant(violation.severity)">
                      {{ formatViolationType(violation.type) }}
                    </Badge>
                    <Badge variant="outline">
                      {{ violation.severity?.toUpperCase() || "UNKNOWN" }}
                    </Badge>
                  </div>
                  <h4 class="font-medium text-foreground mb-1">
                    {{ violation.description }}
                  </h4>
                  <p
                    v-if="violation.date"
                    class="text-sm text-muted-foreground"
                  >
                    Date: {{ formatDate(violation.date) }}
                  </p>
                  <div
                    v-if="violation.details"
                    class="mt-2 text-sm text-muted-foreground"
                  >
                    <div
                      v-for="(value, key) in violation.details"
                      :key="key"
                      class="flex"
                    >
                      <span class="font-medium w-24"
                        >{{ formatDetailKey(key) }}:</span
                      >
                      <span>{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <CheckIcon class="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-foreground mb-2">
              No Violations Found
            </h3>
            <p class="text-muted-foreground">
              Excellent! This audit shows full FMCSA compliance.
            </p>
          </div>
        </CardContent>
      </Card>

      <!-- File Analysis -->
      <Card>
        <CardHeader>
          <h2 class="text-xl font-bold text-foreground">File Analysis</h2>
          <p class="text-sm text-muted-foreground">
            AI-extracted data from uploaded documents
          </p>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div
              v-for="file in audit.files"
              :key="file.id"
              class="p-4 border rounded-lg bg-muted/30"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-3">
                  <DocumentIcon class="w-5 h-5 text-muted-foreground" />
                  <span class="font-medium">{{ file.name }}</span>
                  <span class="text-sm text-muted-foreground">
                    ({{ formatFileSize(file.size) }})
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Processing Log -->
      <Card>
        <CardHeader>
          <h2 class="text-xl font-bold text-foreground">Processing Log</h2>
          <p class="text-sm text-muted-foreground">
            AI engine processing steps and results
          </p>
        </CardHeader>
        <CardContent>
          <div
            v-if="audit.processingLog && audit.processingLog.length > 0"
            class="space-y-2"
          >
            <div
              v-for="(log, index) in audit.processingLog"
              :key="index"
              class="flex items-start space-x-3 p-3 rounded-lg"
              :class="getLogEntryClass(log.type)"
            >
              <div
                class="flex-shrink-0 w-2 h-2 rounded-full mt-2"
                :class="getLogDotClass(log.type)"
              ></div>
              <div class="flex-1">
                <p class="text-sm text-foreground">{{ log.message }}</p>
                <p class="text-xs text-muted-foreground">
                  {{ formatTimestamp(log.timestamp) }}
                </p>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-muted-foreground">
            No processing log available
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <WarningIcon class="w-16 h-16 text-amber-500 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-foreground mb-2">
        Error Loading Audit
      </h3>
      <p class="text-muted-foreground mb-4">{{ error }}</p>
      <Button @click="loadAudit">Try Again</Button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuditStore } from "../stores/audit";
import { useAlert } from "../composables/useAlert";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";
import {
  DownloadIcon,
  DocumentIcon,
  CheckIcon,
  WarningIcon,
} from "@/assets/icons";

const route = useRoute();
const auditStore = useAuditStore();
const { showError } = useAlert();

const audit = ref(null);
const isLoading = ref(true);
const error = ref(null);

// Computed properties for the circular progress
const circumference = computed(() => 2 * Math.PI * 40);
const strokeDashoffset = computed(() => {
  const score = audit.value?.summary?.complianceScore || 0;
  return circumference.value - (score / 100) * circumference.value;
});

onMounted(async () => {
  await loadAudit();
});

const loadAudit = async () => {
  const auditId = route.params.id;
  if (!auditId) {
    error.value = "No audit ID provided";
    isLoading.value = false;
    return;
  }

  try {
    isLoading.value = true;
    error.value = null;

    const result = await auditStore.fetchAudit(auditId);
    if (result.success) {
      audit.value = result.audit;
    } else {
      error.value = result.error || "Failed to load audit";
    }
  } catch (err) {
    error.value = err.message || "An error occurred";
  } finally {
    isLoading.value = false;
  }
};

const formatViolationType = (type) => {
  return (
    type?.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()) ||
    "Unknown"
  );
};

const getViolationVariant = (severity) => {
  switch (severity?.toLowerCase()) {
    case "high":
      return "destructive";
    case "medium":
      return "default";
    case "low":
      return "secondary";
    default:
      return "outline";
  }
};

const getViolationBorderClass = (severity) => {
  switch (severity?.toLowerCase()) {
    case "high":
      return "border-red-200 bg-red-50";
    case "medium":
      return "border-amber-200 bg-amber-50";
    case "low":
      return "border-blue-200 bg-blue-50";
    default:
      return "border-gray-200 bg-gray-50";
  }
};

const getLogEntryClass = (type) => {
  switch (type) {
    case "info":
      return "bg-blue-50 border border-blue-200";
    case "warning":
      return "bg-amber-50 border border-amber-200";
    case "success":
      return "bg-green-50 border border-green-200";
    default:
      return "bg-gray-50 border border-gray-200";
  }
};

const getLogDotClass = (type) => {
  switch (type) {
    case "info":
      return "bg-blue-500";
    case "warning":
      return "bg-amber-500";
    case "success":
      return "bg-green-500";
    default:
      return "bg-gray-500";
  }
};

const formatDetailKey = (key) => {
  return key
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (str) => str.toUpperCase());
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const downloadReport = async () => {
  if (!audit.value?.id) return;

  try {
    await auditStore.downloadReport(audit.value.id);
  } catch (error) {
    console.error("Failed to download report:", error);
    showError("Download Failed", "Failed to download report");
  }
};

const downloadFiles = async () => {
  if (!audit.value?.id) return;

  try {
    await auditStore.downloadFiles(audit.value.id);
  } catch (error) {
    console.error("Failed to download files:", error);
    showError("Download Failed", "Failed to download files");
  }
};
</script>
