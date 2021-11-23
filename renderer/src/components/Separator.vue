<script setup lang="ts">

  const props = defineProps<{
		orientation: 'horizontal' | 'vertical',
	}>()

  // https://www.digitala11y.com/separator-role/

</script>

<template>
  <div role="separator" :aria-orientation="props.orientation" tabindex="-1">
    <div class="handle"></div>
  </div>
</template>

<style scoped>

  [role="separator"] {
    background-color: #ccc;
    cursor: col-resize;
    flex: 0 0 1px;
    position: relative;
  }

  [aria-orientation="horizontal"] {
    cursor: row-resize;
  }

  [aria-orientation="vertical"] {
    cursor: col-resize;
  }

  .handle {
    position: absolute;
    left: -1px;
    right: -1px;
    top: -1px;
    bottom: -1px;
  }

</style>
