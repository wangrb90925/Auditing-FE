<template>
  <div class="debug-panel" v-if="showDebug">
    <div class="debug-header">
      <h3>Frontend Debug Panel</h3>
      <button @click="showDebug = false" class="close-btn">×</button>
    </div>
    
    <div class="debug-content">
      <div class="debug-section">
        <h4>Authentication Status</h4>
        <p>Is Authenticated: {{ userStore.isAuthenticated }}</p>
        <p>User Role: {{ userStore.user?.role || 'None' }}</p>
        <p>Token: {{ userStore.accessToken ? 'Present' : 'Missing' }}</p>
      </div>
      
      <div class="debug-section">
        <h4>Audit Store Status</h4>
        <p>Audits Count: {{ auditStore.audits?.length || 0 }}</p>
        <p>Is Loading: {{ auditStore.isLoading }}</p>
        <p>Error: {{ auditStore.error || 'None' }}</p>
      </div>
      
      <div class="debug-section">
        <h4>API Connection</h4>
        <button @click="testApiConnection">Test API</button>
        <p>API Status: {{ apiStatus }}</p>
      </div>
      
      <div class="debug-section">
        <h4>Console Errors</h4>
        <button @click="clearConsole">Clear Console</button>
        <p>Error Count: {{ errorCount }}</p>
      </div>
    </div>
  </div>
  
  <button 
    v-if="!showDebug" 
    @click="showDebug = true" 
    class="debug-toggle"
    title="Show Debug Panel"
  >
    🐛
  </button>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import { useAuditStore } from '../stores/audit';

export default {
  name: 'DebugPanel',
  setup() {
    const showDebug = ref(false);
    const apiStatus = ref('Unknown');
    const errorCount = ref(0);
    
    const userStore = useUserStore();
    const auditStore = useAuditStore();
    
    const testApiConnection = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/health');
        if (response.ok) {
          apiStatus.value = 'Connected';
        } else {
          apiStatus.value = `Error: ${response.status}`;
        }
      } catch (error) {
        apiStatus.value = `Failed: ${error.message}`;
      }
    };
    
    const clearConsole = () => {
      console.clear();
      errorCount.value = 0;
    };
    
    // Monitor console errors
    const originalError = console.error;
    console.error = function(...args) {
      errorCount.value++;
      originalError.apply(console, args);
    };
    
    onMounted(() => {
      testApiConnection();
    });
    
    return {
      showDebug,
      apiStatus,
      errorCount,
      userStore,
      auditStore,
      testApiConnection,
      clearConsole
    };
  }
};
</script>

<style scoped>
.debug-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 300px;
  background: #1a1a1a;
  color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  z-index: 9999;
  font-family: monospace;
  font-size: 12px;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #333;
  border-radius: 8px 8px 0 0;
}

.debug-header h3 {
  margin: 0;
  font-size: 14px;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
}

.debug-content {
  padding: 10px;
}

.debug-section {
  margin-bottom: 15px;
  padding: 8px;
  background: #2a2a2a;
  border-radius: 4px;
}

.debug-section h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #4CAF50;
}

.debug-section p {
  margin: 4px 0;
  font-size: 11px;
}

.debug-section button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 10px;
  margin-right: 5px;
}

.debug-section button:hover {
  background: #45a049;
}

.debug-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #4CAF50;
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
  z-index: 9998;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.debug-toggle:hover {
  background: #45a049;
}
</style>
