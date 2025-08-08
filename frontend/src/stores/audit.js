import { ref, computed } from "vue";

const audits = ref([]);
const isLoading = ref(false);
const error = ref(null);

// API base URL - change this to match your backend URL
const API_BASE_URL = "http://localhost:5000/api";

export const useAuditStore = () => {
  const createAudit = async (auditData) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await fetch(`${API_BASE_URL}/audits`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          driverName: auditData.driverName,
          driverType: auditData.driverType,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newAudit = await response.json();
      audits.value.push(newAudit);

      return newAudit;
    } catch (err) {
      error.value = err.message;
      console.error("Error creating audit:", err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const uploadFiles = async (auditId, files) => {
    try {
      isLoading.value = true;
      error.value = null;

      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(`${API_BASE_URL}/audits/${auditId}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Update the audit with file information
      const auditIndex = audits.value.findIndex((a) => a.id === auditId);
      if (auditIndex !== -1) {
        audits.value[auditIndex].files = result.files;
        audits.value[auditIndex].updatedAt = new Date().toISOString();
      }

      return result;
    } catch (err) {
      error.value = err.message;
      console.error("Error uploading files:", err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const processAudit = async (auditId) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await fetch(
        `${API_BASE_URL}/audits/${auditId}/process`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const processedAudit = await response.json();

      // Update the audit with processing results
      const auditIndex = audits.value.findIndex((a) => a.id === auditId);
      if (auditIndex !== -1) {
        audits.value[auditIndex] = processedAudit;
      }

      return processedAudit;
    } catch (err) {
      error.value = err.message;
      console.error("Error processing audit:", err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchAudits = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await fetch(`${API_BASE_URL}/audits`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const auditsData = await response.json();
      audits.value = auditsData;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching audits:", err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getAuditById = (id) => {
    return audits.value.find((audit) => audit.id === id);
  };

  const fetchAuditById = async (id) => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await fetch(`${API_BASE_URL}/audits/${id}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const audit = await response.json();

      // Update or add the audit to the store
      const auditIndex = audits.value.findIndex((a) => a.id === id);
      if (auditIndex !== -1) {
        audits.value[auditIndex] = audit;
      } else {
        audits.value.push(audit);
      }

      return audit;
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching audit:", err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const downloadReport = async (auditId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/audits/${auditId}/report`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `fmcsa-audit-${auditId}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      error.value = err.message;
      console.error("Error downloading report:", err);
      throw err;
    }
  };

  const getStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      error.value = err.message;
      console.error("Error fetching stats:", err);
      throw err;
    }
  };

  // Computed properties
  const pendingAudits = computed(() => {
    if (!audits.value || !Array.isArray(audits.value)) {
      return [];
    }
    return audits.value.filter((audit) => audit.status === "pending");
  });

  const completedAudits = computed(() => {
    if (!audits.value || !Array.isArray(audits.value)) {
      return [];
    }
    return audits.value.filter((audit) => audit.status === "completed");
  });

  const processingAudits = computed(() => {
    if (!audits.value || !Array.isArray(audits.value)) {
      return [];
    }
    return audits.value.filter((audit) => audit.status === "processing");
  });

  const failedAudits = computed(() => {
    if (!audits.value || !Array.isArray(audits.value)) {
      return [];
    }
    return audits.value.filter((audit) => audit.status === "failed");
  });

  // Legacy mock data for fallback (remove in production)
  const initializeMockData = () => {
    if (audits.value.length === 0) {
      audits.value = [
        {
          id: "1",
          driverName: "John Smith",
          driverType: "long-haul",
          status: "completed",
          createdAt: "2024-01-15T10:30:00Z",
          updatedAt: "2024-01-15T11:45:00Z",
          violations: 3,
          summary: {
            complianceScore: 85,
            severity: "medium",
            totalViolations: 3,
            hosViolations: 2,
            formViolations: 1,
            falsificationViolations: 0,
          },
          violationsList: [
            {
              date: "2024-01-10",
              type: "HOS_DRIVING_HOURS_EXCEEDED",
              description: "Driving hours exceeded 11-hour limit: 12.5 hours",
              severity: "major",
              penalty: "$2,750",
            },
            {
              date: "2024-01-12",
              type: "HOS_ON_DUTY_HOURS_EXCEEDED",
              description: "On-duty hours exceeded 14-hour limit: 15.2 hours",
              severity: "major",
              penalty: "$2,750",
            },
            {
              date: "2024-01-14",
              type: "FORM_MANNER_MISSING_DUTY_STATUS",
              description: "Missing duty status in driver log entry",
              severity: "minor",
              penalty: "$1,000",
            },
          ],
          processingLog: [
            {
              timestamp: "2024-01-15T10:30:00Z",
              type: "info",
              message: "Starting FMCSA compliance analysis",
            },
            {
              timestamp: "2024-01-15T10:35:00Z",
              type: "info",
              message: "Extracted data from 5 files",
            },
            {
              timestamp: "2024-01-15T11:45:00Z",
              type: "success",
              message: "Audit completed with 85% compliance score",
            },
          ],
        },
        {
          id: "2",
          driverName: "Sarah Johnson",
          driverType: "short-haul",
          status: "processing",
          createdAt: "2024-01-16T09:15:00Z",
          updatedAt: "2024-01-16T09:20:00Z",
          violations: 0,
          summary: {
            complianceScore: 0,
            severity: "low",
            totalViolations: 0,
            hosViolations: 0,
            formViolations: 0,
            falsificationViolations: 0,
          },
          violationsList: [],
          processingLog: [
            {
              timestamp: "2024-01-16T09:15:00Z",
              type: "info",
              message: "Starting FMCSA compliance analysis",
            },
            {
              timestamp: "2024-01-16T09:20:00Z",
              type: "info",
              message: "Extracted data from 3 files",
            },
          ],
        },
        {
          id: "3",
          driverName: "Mike Wilson",
          driverType: "exemption",
          status: "pending",
          createdAt: "2024-01-16T14:30:00Z",
          updatedAt: "2024-01-16T14:30:00Z",
          violations: 0,
          summary: {
            complianceScore: 0,
            severity: "low",
            totalViolations: 0,
            hosViolations: 0,
            formViolations: 0,
            falsificationViolations: 0,
          },
          violationsList: [],
          processingLog: [],
        },
      ];
    }
  };

  return {
    // State
    audits,
    isLoading,
    error,

    // Actions
    createAudit,
    uploadFiles,
    processAudit,
    fetchAudits,
    getAuditById,
    fetchAuditById,
    downloadReport,
    getStats,
    initializeMockData,

    // Computed
    pendingAudits,
    completedAudits,
    processingAudits,
    failedAudits,
  };
};
