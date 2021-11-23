<script setup lang="ts">

	import type { Task } from '../lib/task'

	const props = defineProps<{task: Task}>()

	const emit = defineEmits<{
    (event: 'delete'): void
  }>()

	function updateConfig(newConfig: {}) {
    props.task.config = newConfig
	}


</script>

<template>
  <section class="task">
    <header>
      <h1>{{ props.task.title }}</h1>
      <button class="delete">
        <span class="material-icons" @click="emit('delete')">delete</span>
      </button>
    </header>
    <main>
      <component
        :is="props.task.type.component"
        :task="props.task"
      />
    </main>
    <footer>
      Status: {{ props.task.status }}
    </footer>
  </section>
</template>

<style scoped>

	section {
		border: 1px solid #aaa;
		display: flex;
		flex-direction: column;
		margin: 1em;
	}

	header {
    align-items: center;
		background: #f8f8f8;
		display: flex;
    height: 40px;
	}

	header button {
		background: transparent;
		border: 0;
    margin: 0;
    padding: 8px;
	}

  header button:hover {
    background-color: rgba(0, 0, 0, 0.1);
    color: #f00;
  }

	h1 {
		flex: 1;
    font-size: 100%;
		margin: 0;
    overflow: hidden;
    padding: 0 0.25em;
    text-overflow: ellipsis;
	}

  main {
    padding: 1em;
  }

  footer {
		background: #f8f8f8;
    font-size: 13px;
    line-height: 22px;
  }

</style>
