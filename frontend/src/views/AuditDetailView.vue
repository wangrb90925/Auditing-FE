<template>
  <div v-if="audit" class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Audit Details</h1>
        <p class="text-gray-600">Driver: {{ audit.driverName }}</p>
      </div>
      <div class="flex space-x-3">
        <Button
          v-if="audit.status === 'completed'"
          @click="downloadReport"
          variant="default"
        >
          <DownloadIcon class="w-4 h-4 mr-2" />
          Download Report
        </Button>
        <Button variant="outline" as-child>
          <router-link to="/audits" class="flex items-center">
            <ArrowLeftIcon class="w-4 h-4 mr-2" />
            Back to Audits
          </router-link>
        </Button>
      </div>
    </div>

    <!-- Status Banner -->
    <Card>
      <CardContent class="p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                :class="getStatusIconClasses(audit.status)"
                class="w-8 h-8 rounded-full flex items-center justify-center"
              >
                <ClockIcon v-if="audit.status === 'pending'" class="w-5 h-5" />
                <RefreshIcon
                  v-else-if="audit.status === 'processing'"
                  class="w-5 h-5"
                />
                <CheckIcon
                  v-else-if="audit.status === 'completed'"
                  class="w-5 h-5"
                />
                <WarningIcon v-else class="w-5 h-5" />
              </div>
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">
                {{ formatStatus(audit.status) }}
              </h3>
              <p class="text-sm text-gray-500">
                Created {{ formatDate(audit.createdAt) }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <Badge :variant="getStatusVariant(audit.status)">
              {{ formatStatus(audit.status) }}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Audit Information -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Basic Info -->
      <Card>
        <CardHeader>
          <h3 class="text-lg font-semibold text-gray-900">Audit Information</h3>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div>
              <Label class="text-sm font-medium text-gray-500"
                >Driver Name</Label
              >
              <p class="text-sm text-gray-900">{{ audit.driverName }}</p>
            </div>
            <div>
              <Label class="text-sm font-medium text-gray-500"
                >Driver Type</Label
              >
              <p class="text-sm text-gray-900">
                {{ formatDriverType(audit.driverType) }}
              </p>
            </div>
            <div>
              <Label class="text-sm font-medium text-gray-500"
                >Files Processed</Label
              >
              <p class="text-sm text-gray-900">
                {{ audit.files.length }} files
              </p>
              <div class="mt-1 space-y-1">
                <div
                  v-for="file in audit.files"
                  :key="file"
                  class="text-xs text-gray-500"
                >
                  • {{ file }}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Compliance Score -->
      <Card v-if="audit.summary">
        <CardHeader>
          <h3 class="text-lg font-semibold text-gray-900">Compliance Score</h3>
        </CardHeader>
        <CardContent>
          <div class="text-center">
            <div
              class="relative inline-flex items-center justify-center w-24 h-24 rounded-full bg-gray-100"
            >
              <div
                :class="getComplianceColor(audit.summary.complianceScore)"
                class="absolute inset-0 rounded-full flex items-center justify-center"
              >
                <span class="text-2xl font-bold text-white"
                  >{{ audit.summary.complianceScore }}%</span
                >
              </div>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              {{ getComplianceMessage(audit.summary.complianceScore) }}
            </p>
          </div>
        </CardContent>
      </Card>

      <!-- Violations Summary -->
      <Card>
        <CardHeader>
          <h3 class="text-lg font-semibold text-gray-900">
            Violations Summary
          </h3>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Total Violations</span>
              <span class="text-sm font-medium text-gray-900">{{
                audit.violations || 0
              }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Severity Level</span>
              <Badge :variant="getSeverityVariant(audit.summary?.severity)">
                {{ formatSeverity(audit.summary?.severity) }}
              </Badge>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">Processing Time</span>
              <span class="text-sm text-gray-900">{{
                getProcessingTime(audit.createdAt, audit.updatedAt)
              }}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Violations Details -->
    <Card v-if="audit.violationsList && audit.violationsList.length > 0">
      <CardHeader>
        <h3 class="text-lg font-semibold text-gray-900">Violations Details</h3>
      </CardHeader>
      <CardContent>
        <div class="space-y-4">
          <div
            v-for="(violation, index) in audit.violationsList"
            :key="index"
            class="border border-gray-200 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-medium text-gray-900">
                  {{ violation.rule }}
                </h4>
                <p class="text-sm text-gray-600 mt-1">
                  {{ violation.description }}
                </p>
                <div class="mt-2 flex items-center space-x-4">
                  <Badge
                    :variant="getViolationSeverityVariant(violation.severity)"
                  >
                    {{ formatViolationSeverity(violation.severity) }}
                  </Badge>
                  <span class="text-xs text-gray-500">
                    Section: {{ violation.section }}
                  </span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-sm font-medium text-gray-900">
                  {{ violation.penalty }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Processing Log -->
    <Card v-if="audit.processingLog && audit.processingLog.length > 0">
      <CardHeader>
        <h3 class="text-lg font-semibold text-gray-900">Processing Log</h3>
      </CardHeader>
      <CardContent>
        <div class="space-y-3">
          <div
            v-for="(log, index) in audit.processingLog"
            :key="index"
            class="flex items-start space-x-3"
          >
            <div
              :class="getLogIconClasses(log.type)"
              class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center"
            >
              <InfoIcon v-if="log.type === 'info'" class="w-4 h-4" />
              <WarningIcon v-else-if="log.type === 'warning'" class="w-4 h-4" />
              <CheckIcon v-else class="w-4 h-4" />
            </div>
            <div class="flex-1">
              <p class="text-sm text-gray-900">{{ log.message }}</p>
              <p class="text-xs text-gray-500">
                {{ formatTime(log.timestamp) }}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>

  <!-- Loading State -->
  <div v-else class="flex items-center justify-center py-12">
    <div class="text-center">
      <RefreshIcon class="mx-auto h-12 w-12 text-gray-400 animate-spin" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">Loading audit...</h3>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuditStore } from "../stores/audit";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";
import Label from "@/components/ui/label.vue";
import {
  DownloadIcon,
  ArrowLeftIcon,
  ClockIcon,
  RefreshIcon,
  CheckIcon,
  WarningIcon,
  InfoIcon,
} from "@/assets/icons";

const route = useRoute();
const router = useRouter();
const auditStore = useAuditStore();

const audit = computed(() => {
  return auditStore.getAuditById(route.params.id);
});

onMounted(() => {
  if (!audit.value) {
    router.push("/audits");
  }
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

const getStatusIconClasses = (status) => {
  const classes = {
    pending: "bg-warning-100 text-warning-600",
    processing: "bg-primary-100 text-primary-600",
    completed: "bg-success-100 text-success-600",
    failed: "bg-danger-100 text-danger-600",
  };
  return classes[status] || "bg-gray-100 text-gray-600";
};

const getComplianceColor = (score) => {
  if (score >= 80) return "bg-success-500";
  if (score >= 60) return "bg-warning-500";
  return "bg-danger-500";
};

const getComplianceMessage = (score) => {
  if (score >= 80) return "Excellent compliance";
  if (score >= 60) return "Good compliance";
  return "Needs improvement";
};

const formatSeverity = (severity) => {
  const severities = {
    low: "Low",
    medium: "Medium",
    high: "High",
    critical: "Critical",
  };
  return severities[severity] || "Unknown";
};

const getSeverityVariant = (severity) => {
  const variants = {
    low: "secondary",
    medium: "default",
    high: "destructive",
    critical: "destructive",
  };
  return variants[severity] || "secondary";
};

const getViolationSeverityVariant = (severity) => {
  const variants = {
    minor: "secondary",
    moderate: "default",
    major: "destructive",
    critical: "destructive",
  };
  return variants[severity] || "secondary";
};

const formatViolationSeverity = (severity) => {
  const severities = {
    minor: "Minor",
    moderate: "Moderate",
    major: "Major",
    critical: "Critical",
  };
  return severities[severity] || "Unknown";
};

const getLogIconClasses = (type) => {
  const classes = {
    info: "bg-info-100 text-info-600",
    warning: "bg-warning-100 text-warning-600",
    success: "bg-success-100 text-success-600",
  };
  return classes[type] || "bg-gray-100 text-gray-600";
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
};

const getProcessingTime = (createdAt, updatedAt) => {
  const start = new Date(createdAt);
  const end = new Date(updatedAt);
  const diff = end - start;
  const minutes = Math.floor(diff / 60000);
  return `${minutes} minutes`;
};

const downloadReport = () => {
  if (!audit.value) return;

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
      audit.value.driverName,
      formatDriverType(audit.value.driverType),
      formatStatus(audit.value.status),
      audit.value.violations || 0,
      audit.value.summary?.complianceScore || "N/A",
      formatDate(audit.value.createdAt),
    ],
  ]
    .map((row) => row.join(","))
    .join("\n");

  // Create and download file
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `audit-${audit.value.id}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};
</script>
