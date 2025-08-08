<template>
  <svg :class="className" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M6 18L18 6M6 6l12 12"
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
