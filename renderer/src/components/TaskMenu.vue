<script setup lang="ts">

	import { categories } from '../task_types'
  import type { TaskConstructor } from '../lib/task';

  const emit = defineEmits<{
    (event: 'select', task: TaskConstructor): void
  }>()

</script>

<template>
  <div role="tree">
    <div role="group" v-for="category in categories">
      <div class="label">{{ category.label }}</div>
      <div role="treeitem" v-for="taskType in category.tasks" @click="emit('select', taskType)">
        {{ taskType.label }}
      </div>
    </div>
  </div>
</template>

<style scoped>

  [role='tree'] {
    background-color: #f8f8f8;
  }

  .label {
    white-space: nowrap;
  }

  [role='group'] {
    margin: 11px 0 0;
  }

  [role='group'] > .label {
    color: #999;
    font-size: 11px;
    font-weight: bold;
    line-height: 22px;
    padding: 0 8px;
    text-transform: uppercase;
  }

  [role='treeitem'] {
    font-size: 13px;
    line-height: 22px;
    padding: 0 8px;
  }

  [role='treeitem']:hover {
    background-color: #e8e8e8;
  }

  [role='tooltip'] {
    display: none;
  }

</style>
