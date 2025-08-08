<template>
  <svg :class="className" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"
    />
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z"
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
