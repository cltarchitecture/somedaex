<script setup lang="ts">

	import { ipcRenderer } from 'electron'
	import { basename, dirname, extname } from 'path'
	import type LoadFile from './LoadFile'

	const props = defineProps<{
		task: LoadFile
	}>()

	async function selectFile() {
		const result = await ipcRenderer.invoke('showOpenDialog', {
			title: 'Select a file',
			filters: [
				{name: 'Supported Files', extensions: ['arrow', 'csv', 'fea', 'feather', 'jsonl', 'parquet', 'tsv']},
				{name: 'All Files', extensions: ['*']}
			]
		})

		if (result.filePaths.length > 0) {
      const path = result.filePaths[0]
      let format = extname(path).substr(1)
      if (format == 'tsv') {
        format = 'csv'
      } else if (format == 'fea' || format == 'feather') {
        format = 'arrow'
      }

      props.task.config = {path, format}
		}
	}

</script>

<template>
	<div>
		<template v-if="props.task.config.path">
			<span class="path">{{ dirname(props.task.config.path) }}</span>
			<span class="name">{{ basename(props.task.config.path) }}</span>
		</template>
		<button @click="selectFile">Select File</button>
	</div>
</template>

<style scoped>

	div {
		align-items: center;
		display: flex;
	}

	.path {
		flex: 0 1 auto;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.name {
		flex: 1 0 auto;
	}

	.name:before {
		content: '/';
	}

	button {
		margin-left: 1em;
	}


</style>
