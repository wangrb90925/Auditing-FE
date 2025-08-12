import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { apiService } from "../lib/api";

export const useAuditStore = defineStore("audit", () => {
  const audits = ref([]);
  const currentAudit = ref(null);
  const stats = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // Computed properties
  const completedAudits = computed(() =>
    audits.value.filter((audit) => audit.status === "completed")
  );

  const pendingAudits = computed(() =>
    audits.value.filter((audit) => audit.status === "pending")
  );

  const processingAudits = computed(() =>
    audits.value.filter((audit) => audit.status === "processing")
  );

  // Create new audit
  const createAudit = async (auditData) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.createAudit(auditData);
      audits.value.unshift(response);

      return { success: true, audit: response };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Get all audits
  const fetchAudits = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.getAudits();
      audits.value = response;

      return { success: true, audits: response };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Get specific audit
  const fetchAudit = async (auditId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.getAudit(auditId);
      currentAudit.value = response;

      return { success: true, audit: response };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Upload files for an audit
  const uploadFiles = async (auditId, files) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.uploadFiles(auditId, files);

      // Update the audit in the list
      const auditIndex = audits.value.findIndex(
        (audit) => audit.id === auditId
      );
      if (auditIndex !== -1) {
        audits.value[auditIndex].files = [
          ...audits.value[auditIndex].files,
          ...response.files,
        ];
      }

      // Update current audit if it's the same
      if (currentAudit.value?.id === auditId) {
        currentAudit.value.files = [
          ...currentAudit.value.files,
          ...response.files,
        ];
      }

      return { success: true, files: response.files };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Process audit
  const processAudit = async (auditId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.processAudit(auditId);

      // Update the audit in the list
      const auditIndex = audits.value.findIndex(
        (audit) => audit.id === auditId
      );
      if (auditIndex !== -1) {
        audits.value[auditIndex] = response;
      }

      // Update current audit if it's the same
      if (currentAudit.value?.id === auditId) {
        currentAudit.value = response;
      }

      return { success: true, audit: response };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Download report
  const downloadReport = async (auditId) => {
    try {
      error.value = null;

      const blob = await apiService.downloadReport(auditId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `fmcsa_audit_${auditId}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { success: true };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    }
  };

  // Download files
  const downloadFiles = async (auditId) => {
    try {
      error.value = null;

      const blob = await apiService.downloadFiles(auditId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `audit_files_${auditId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { success: true };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    }
  };

  // Get statistics
  const fetchStats = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await apiService.getStats();
      stats.value = response;

      return { success: true, stats: response };
    } catch (err) {
      error.value = err.message;
      return { success: false, error: err.message };
    } finally {
      isLoading.value = false;
    }
  };

  // Clear error
  const clearError = () => {
    error.value = null;
  };

  // Clear current audit
  const clearCurrentAudit = () => {
    currentAudit.value = null;
  };

  return {
    // State
    audits,
    currentAudit,
    stats,
    isLoading,
    error,

    // Computed
    completedAudits,
    pendingAudits,
    processingAudits,

    // Actions
    createAudit,
    fetchAudits,
    fetchAudit,
    uploadFiles,
    processAudit,
    downloadReport,
    downloadFiles,
    fetchStats,
    clearError,
    clearCurrentAudit,
  };
});
