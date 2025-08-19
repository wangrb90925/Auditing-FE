// Use environment variable for API base URL with fallback
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get auth headers with token
  getAuthHeaders() {
    const token = localStorage.getItem(
      import.meta.env.VITE_JWT_STORAGE_KEY || "access_token"
    );
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // Handle API responses
  async handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
      let errorMessage = data.error || `HTTP error! status: ${response.status}`;

      // Provide more specific error messages for common status codes
      switch (response.status) {
        case 401:
          errorMessage = "Unauthorized: Please log in again";
          break;
        case 403:
          errorMessage =
            "Forbidden: You don't have permission to access this resource";
          break;
        case 422:
          errorMessage = "Validation error: The request could not be processed";
          break;
        case 500:
          errorMessage = "Server error: Please try again later";
          break;
      }

      throw new Error(errorMessage);
    }

    return data;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getAuthHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      return await this.handleResponse(response);
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Authentication endpoints
  async login(credentials) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async register(userData) {
    // Split full name into first and last name
    const nameParts = userData.fullName.trim().split(" ");
    const firstName = nameParts[0] || "";
    const lastName = nameParts.slice(1).join(" ") || "";

    const payload = {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      first_name: firstName,
      last_name: lastName,
      role: userData.role,
    };

    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getProfile() {
    return this.request("/auth/profile");
  }

  async updateProfile(profileData) {
    return this.request("/auth/profile", {
      method: "PUT",
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData) {
    return this.request("/auth/change-password", {
      method: "POST",
      body: JSON.stringify(passwordData),
    });
  }

  // Admin endpoints
  async getUsers() {
    return this.request("/admin/users");
  }

  async changeUserRole(userId, role) {
    return this.request(`/admin/users/${userId}/role`, {
      method: "PUT",
      body: JSON.stringify({ role }),
    });
  }

  // Audit endpoints
  async createAudit(auditData) {
    try {
      const response = await this.request("/audits", {
        method: "POST",
        body: JSON.stringify(auditData),
      });

      // Validate response structure
      if (!response || !response.id) {
        console.error("Invalid response from createAudit:", response);
        throw new Error("Invalid response from server: missing audit ID");
      }

      return response;
    } catch (error) {
      console.error("Error in createAudit:", error);
      throw error;
    }
  }

  async getAudits() {
    return this.request("/audits");
  }

  async getAudit(auditId) {
    return this.request(`/audits/${auditId}`);
  }

  async deleteAudit(auditId) {
    return this.request(`/audits/${auditId}`, {
      method: "DELETE",
    });
  }

  async uploadFiles(auditId, files) {
    try {
      // Validate auditId
      if (!auditId || auditId === "undefined" || auditId === "null") {
        throw new Error(`Invalid audit ID: ${auditId}`);
      }

      console.log("Uploading files for audit ID:", auditId);

      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });

      const token = localStorage.getItem("access_token");
      const url = `${this.baseURL}/audits/${auditId}/upload`;

      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      return this.handleResponse(response);
    } catch (error) {
      console.error("Error in uploadFiles:", error);
      throw error;
    }
  }

  async processAudit(auditId) {
    try {
      // Validate auditId
      if (!auditId || auditId === "undefined" || auditId === "null") {
        throw new Error(`Invalid audit ID: ${auditId}`);
      }

      console.log("Processing audit with ID:", auditId);
      return this.request(`/audits/${auditId}/process`, {
        method: "POST",
      });
    } catch (error) {
      console.error("Error in processAudit:", error);
      throw error;
    }
  }

  async downloadReport(auditId) {
    const token = localStorage.getItem("access_token");
    const url = `${this.baseURL}/audits/${auditId}/report`;

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to download report");
    }

    return response.blob();
  }

  async downloadFiles(auditId) {
    const token = localStorage.getItem("access_token");
    const url = `${this.baseURL}/audits/${auditId}/files`;

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to download files");
    }

    return response.blob();
  }

  async getStats() {
    return this.request("/stats");
  }

  // Health check
  async healthCheck() {
    return this.request("/health");
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing purposes
export default ApiService;
