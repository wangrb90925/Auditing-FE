<template>
  <div
    :class="
      cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        {
          'border-transparent bg-primary text-primary-foreground hover:bg-primary/80':
            variant === 'default',
          'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80':
            variant === 'secondary',
          'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80':
            variant === 'destructive',
          'text-muted-foreground': variant === 'outline',
        },
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>

<script setup>
import { cn } from "@/lib/utils";

defineProps({
  variant: {
    type: String,
    default: "default",
    validator: (value) =>
      ["default", "secondary", "destructive", "outline"].includes(value),
  },
});
</script>
