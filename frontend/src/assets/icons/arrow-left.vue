<template>
  <svg :class="className" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M10 19l-7-7m0 0l7-7m-7 7h18"
    />
  </svg>
</template>

<script setup>
defineProps({
  className: {
    type: String,
    default: "w-4 h-4",
  },
});
</script>
