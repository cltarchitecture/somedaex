<script setup lang="ts">

  import type { Task, TaskConstructor } from '../lib/task'
  import { Workspace } from '../lib/workspace'
  import Separator from './Separator.vue';
  import TaskMenu from './TaskMenu.vue';
	import TaskInfo from './TaskInfo.vue'

  const workspace = new Workspace()

	function addTask(type: TaskConstructor) {
		workspace.addTask(type)
	}

  function deleteTask(task: Task) {
    workspace.deleteTask(task)
  }

</script>

<template>
  <TaskMenu @select="addTask"/>
  <Separator orientation="vertical"/>
  <div class="pipeline">
    <TaskInfo v-for="(task, id) in workspace.pipeline" :key="id" :task="task" @delete="deleteTask(task)"/>
  </div>
  <!-- <Separator orientation="vertical"/>
  <div class="visualization-area"></div> -->
</template>

<style scoped>

  .pipeline {
    flex: 1;
    overflow: auto;
  }

  .visualization-area {
    flex: 1
  }

</style>
