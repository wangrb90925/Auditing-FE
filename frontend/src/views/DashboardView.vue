<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-foreground mb-2">
          FMCSA Compliance Dashboard
        </h1>
        <p class="text-muted-foreground text-lg">
          Hours-of-Service (HOS) audit overview and violation tracking
        </p>
      </div>
      <Button
        as-child
        class="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg"
      >
        <router-link to="/upload" class="flex items-center">
          <PlusIcon class="w-4 h-4 mr-2" />
          New HOS Audit
        </router-link>
      </Button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card
        class="bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200/50 dark:border-blue-800/50"
      >
        <CardContent class="p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <ChartIcon class="w-6 h-6 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-blue-600 dark:text-blue-400">
                Total Audits
              </p>
              <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">
                {{ audits.length }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-amber-50 to-amber-100/50 dark:from-amber-950/50 dark:to-amber-900/30 border-amber-200/50 dark:border-amber-800/50"
      >
        <CardContent class="p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <ClockIcon class="w-6 h-6 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-amber-600 dark:text-amber-400">
                Pending Review
              </p>
              <p class="text-3xl font-bold text-amber-900 dark:text-amber-100">
                {{ auditStore.pendingAudits.length }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/50 dark:to-green-900/30 border-green-200/50 dark:border-green-800/50"
      >
        <CardContent class="p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <CheckIcon class="w-6 h-6 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-green-600 dark:text-green-400">
                HOS Compliant
              </p>
              <p class="text-3xl font-bold text-green-900 dark:text-green-100">
                {{ auditStore.completedAudits.length }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/50 dark:to-red-900/30 border-red-200/50 dark:border-red-800/50"
      >
        <CardContent class="p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div
                class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <WarningIcon class="w-6 h-6 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-red-600 dark:text-red-400">
                HOS Violations
              </p>
              <p class="text-3xl font-bold text-red-900 dark:text-red-100">
                {{ totalViolations }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Recent Audits -->
    <Card class="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-xl font-bold text-foreground">Recent HOS Audits</h2>
            <p class="text-sm text-muted-foreground mt-1">
              Latest FMCSA compliance assessments
            </p>
          </div>
          <Button variant="outline" as-child class="rounded-lg">
            <router-link to="/audits">View all</router-link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-border/50">
            <thead class="bg-muted/30">
              <tr>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  Driver
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  Type
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  Status
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  HOS Violations
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  Date
                </th>
                <th
                  class="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-transparent divide-y divide-border/30">
              <tr
                v-for="audit in recentAudits"
                :key="audit.id"
                class="hover:bg-muted/20 transition-colors duration-200"
              >
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground"
                >
                  {{ audit.driverName }}
                </td>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ formatDriverType(audit.driverType) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge
                    :variant="getStatusVariant(audit.status)"
                    class="rounded-full"
                  >
                    {{ formatStatus(audit.status) }}
                  </Badge>
                </td>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ audit.violations || 0 }}
                </td>
                <td
                  class="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground"
                >
                  {{ formatDate(audit.createdAt) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      as-child
                      class="rounded-lg"
                    >
                      <router-link :to="`/audit/${audit.id}`">View</router-link>
                    </Button>
                    <Button
                      v-if="audit.status === 'completed'"
                      variant="outline"
                      size="sm"
                      @click="downloadReport(audit.id)"
                      class="rounded-lg"
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
      </CardContent>
    </Card>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 !mb-20">
      <Card
        class="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20 hover:shadow-lg transition-all duration-300 group"
      >
        <CardContent class="p-8">
          <div class="text-center">
            <div
              class="mx-auto w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-shadow duration-300"
            >
              <UploadIcon class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-foreground mb-3">
              Upload Driver Logs
            </h3>
            <p class="text-muted-foreground mb-6 leading-relaxed">
              Upload ELD logs, fuel receipts, and BOLs for AI-powered FMCSA
              compliance auditing
            </p>
            <Button
              as-child
              class="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg rounded-lg"
            >
              <router-link to="/upload">Start HOS Audit</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-green-500/5 to-green-600/10 border-green-200/30 hover:shadow-lg transition-all duration-300 group"
      >
        <CardContent class="p-8">
          <div class="text-center">
            <div
              class="mx-auto w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-shadow duration-300"
            >
              <DocumentIcon class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-foreground mb-3">
              Audit Reports
            </h3>
            <p class="text-muted-foreground mb-6 leading-relaxed">
              Access detailed FMCSA compliance reports with violation analysis
              and export capabilities
            </p>
            <Button
              variant="outline"
              as-child
              class="w-full rounded-lg border-green-200 text-green-700 hover:bg-green-50"
            >
              <router-link to="/audits">View Reports</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        class="bg-gradient-to-br from-amber-500/5 to-amber-600/10 border-amber-200/30 hover:shadow-lg transition-all duration-300 group"
      >
        <CardContent class="p-8">
          <div class="text-center">
            <div
              class="mx-auto w-16 h-16 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-shadow duration-300"
            >
              <InfoIcon class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-foreground mb-3">
              Audit History
            </h3>
            <p class="text-muted-foreground mb-6 leading-relaxed">
              Review past HOS audits and track compliance trends across driver
              types and exemptions
            </p>
            <Button
              variant="outline"
              as-child
              class="w-full rounded-lg border-amber-200 text-amber-700 hover:bg-amber-50"
            >
              <router-link to="/audits">View History</router-link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAuditStore } from "../stores/audit";
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

// Initialize mock data if needed
auditStore.initializeMockData();

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
  return variants[status] || "secondary";
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
