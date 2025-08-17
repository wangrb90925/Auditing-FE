<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ report.title }}</h1>
        <p class="text-gray-600 text-lg">{{ report.description }}</p>
        <p class="text-sm text-gray-500 mt-2">Generated {{ report.generatedAt }}</p>
      </div>
      <div class="flex space-x-3">
        <Button
          variant="outline"
          @click="downloadReport"
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
          <span>Download</span>
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
          <span>Export PDF</span>
        </Button>
      </div>
    </div>

    <!-- Report Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Report Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Executive Summary -->
        <Card>
          <CardHeader>
            <h3 class="text-lg font-semibold text-gray-900">Executive Summary</h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                  <p class="text-2xl font-bold text-blue-600">{{ report.summary.complianceRate }}%</p>
                  <p class="text-sm text-blue-600">Compliance Rate</p>
                </div>
                <div class="text-center p-4 bg-red-50 rounded-lg">
                  <p class="text-2xl font-bold text-red-600">{{ report.summary.totalViolations }}</p>
                  <p class="text-sm text-red-600">Total Violations</p>
                </div>
              </div>
              <p class="text-gray-700">{{ report.summary.description }}</p>
            </div>
          </CardContent>
        </Card>

        <!-- Violations Breakdown -->
        <Card>
          <CardHeader>
            <h3 class="text-lg font-semibold text-gray-900">Violations Breakdown</h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div v-for="violation in report.violations" :key="violation.type" class="flex items-center justify-between p-3 border rounded-lg">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 rounded-full" :class="getViolationColor(violation.severity)"></div>
                  <span class="font-medium text-gray-900">{{ violation.type }}</span>
                </div>
                <div class="text-right">
                  <p class="font-semibold text-gray-900">{{ violation.count }}</p>
                  <p class="text-sm text-gray-500">{{ violation.percentage }}%</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Recommendations -->
        <Card>
          <CardHeader>
            <h3 class="text-lg font-semibold text-gray-900">Recommendations</h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <div v-for="(recommendation, index) in report.recommendations" :key="index" class="flex items-start space-x-3">
                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <p class="text-gray-700">{{ recommendation }}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Report Metadata -->
        <Card>
          <CardHeader>
            <h3 class="text-lg font-semibold text-gray-900">Report Details</h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <div>
                <p class="text-sm font-medium text-gray-500">Report Type</p>
                <p class="text-sm text-gray-900">{{ report.type }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Date Range</p>
                <p class="text-sm text-gray-900">{{ report.dateRange }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Generated By</p>
                <p class="text-sm text-gray-900">{{ report.generatedBy }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">Status</p>
                <Badge :variant="getStatusVariant(report.status)" class="rounded-full">
                  {{ report.status }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Quick Actions -->
        <Card>
          <CardHeader>
            <h3 class="text-lg font-semibold text-gray-900">Quick Actions</h3>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <Button variant="outline" class="w-full" @click="shareReport">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                </svg>
                Share Report
              </Button>
              <Button variant="outline" class="w-full" @click="scheduleReport">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                Schedule Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAlert } from "../composables/useAlert";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import CardHeader from "@/components/ui/card-header.vue";
import CardContent from "@/components/ui/card-content.vue";
import Badge from "@/components/ui/badge.vue";

const route = useRoute();
const router = useRouter();
const { showSuccess, showError } = useAlert();

// Mock report data - in real app this would come from API
const report = ref({
  id: 1,
  title: 'Monthly Compliance Summary',
  description: 'Comprehensive compliance report for August 2024',
  type: 'Compliance Summary',
  dateRange: 'August 1-31, 2024',
  generatedAt: '2 hours ago',
  generatedBy: 'John Doe',
  status: 'completed',
  summary: {
    complianceRate: 87.5,
    totalViolations: 24,
    description: 'Overall compliance has improved by 5% compared to last month. HOS violations remain the primary concern, accounting for 60% of all violations.'
  },
  violations: [
    { type: 'HOS Violations', count: 14, percentage: 58, severity: 'high' },
    { type: 'Form & Manner', count: 6, percentage: 25, severity: 'medium' },
    { type: 'Fuel Receipts', count: 3, percentage: 13, severity: 'low' },
    { type: 'BOL Issues', count: 1, percentage: 4, severity: 'low' }
  ],
  recommendations: [
    'Implement additional driver training on HOS regulations',
    'Review and update fuel receipt collection procedures',
    'Consider implementing automated compliance monitoring tools',
    'Schedule regular compliance review meetings'
  ]
});

const getViolationColor = (severity) => {
  switch (severity) {
    case 'high': return 'bg-red-500';
    case 'medium': return 'bg-yellow-500';
    case 'low': return 'bg-green-500';
    default: return 'bg-gray-500';
  }
};

const getStatusVariant = (status) => {
  switch (status) {
    case 'completed': return 'default';
    case 'pending': return 'secondary';
    case 'failed': return 'destructive';
    default: return 'outline';
  }
};

const downloadReport = () => {
  showSuccess('Download Started', 'Report download has begun.');
};

const exportToPDF = () => {
  showSuccess('Export Started', 'PDF export has begun.');
};

const shareReport = () => {
  showSuccess('Share', 'Report sharing options opened.');
};

const scheduleReport = () => {
  showSuccess('Schedule', 'Report scheduling options opened.');
};

onMounted(() => {
  // Load report data based on route params
  const reportId = route.params.id;
  // In real app, fetch report data from API using reportId
  console.log('Loading report:', reportId);
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
