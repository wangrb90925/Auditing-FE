<template>
  <div v-if="isVisible" class="max-w-md w-full" :class="alertClasses">
    <div
      class="flex items-start space-x-3 p-4 rounded-lg border shadow-lg backdrop-blur-sm"
    >
      <div class="flex-shrink-0">
        <component :is="icon" class="w-5 h-5" :class="iconClasses" />
      </div>
      <div class="flex-1 min-w-0">
        <h3 v-if="title" class="text-sm font-medium text-foreground">
          {{ title }}
        </h3>
        <div v-if="message" class="text-sm text-muted-foreground mt-1">
          <p
            v-for="(line, index) in messageLines"
            :key="index"
            class="mb-1 last:mb-0"
          >
            {{ line }}
          </p>
        </div>
      </div>
      <button
        @click="close"
        class="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
      >
        <XIcon class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { CheckIcon, WarningIcon, InfoIcon, XIcon } from "@/assets/icons";

const props = defineProps({
  type: {
    type: String,
    default: "info",
    validator: (value) =>
      ["success", "error", "warning", "info"].includes(value),
  },
  title: {
    type: String,
    default: "",
  },
  message: {
    type: String,
    default: "",
  },
  duration: {
    type: Number,
    default: 5000,
  },
  persistent: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);
const isVisible = ref(true);

const icon = computed(() => {
  switch (props.type) {
    case "success":
      return CheckIcon;
    case "error":
      return WarningIcon;
    case "warning":
      return WarningIcon;
    case "info":
      return InfoIcon;
    default:
      return InfoIcon;
  }
});

const messageLines = computed(() => {
  if (!props.message) return [];
  return props.message.split("\n").filter((line) => line.trim() !== "");
});

const alertClasses = computed(() => {
  const baseClasses = "animate-in slide-in-from-right-2";

  switch (props.type) {
    case "success":
      return `${baseClasses} bg-green-50/90 border-green-200/50`;
    case "error":
      return `${baseClasses} bg-red-50/90 border-red-200/50`;
    case "warning":
      return `${baseClasses} bg-amber-50/90 border-amber-200/50`;
    case "info":
      return `${baseClasses} bg-blue-50/90 border-blue-200/50`;
    default:
      return `${baseClasses} bg-card/90 border-border/50`;
  }
});

const iconClasses = computed(() => {
  switch (props.type) {
    case "success":
      return "text-green-600";
    case "error":
      return "text-red-600";
    case "warning":
      return "text-amber-600";
    case "info":
      return "text-blue-600";
    default:
      return "text-muted-foreground";
  }
});

const close = () => {
  isVisible.value = false;
  emit("close");
};

onMounted(() => {
  if (!props.persistent && props.duration > 0) {
    setTimeout(() => {
      close();
    }, props.duration);
  }
});
</script>

<style scoped>
.animate-in {
  animation: slideIn 0.3s ease-out;
}

.slide-in-from-right-2 {
  animation: slideInFromRight 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInFromRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
