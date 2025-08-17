<template>
  <div class="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
    <TransitionGroup name="alert" tag="div" class="space-y-2">
      <Alert
        v-for="alert in alerts"
        :key="alert.id"
        :type="alert.type"
        :title="alert.title"
        :message="alert.message"
        :duration="alert.duration"
        :persistent="alert.persistent"
        @close="removeAlert(alert.id)"
        class="pointer-events-auto"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useAlert } from "../composables/useAlert";
import Alert from "./ui/alert.vue";

const { alerts, removeAlert } = useAlert();
</script>

<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: all 0.3s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.alert-move {
  transition: transform 0.3s ease;
}
</style>
