<script setup lang="ts">

  import { Type } from '@apache-arrow/esnext-cjs'
	import SelectColumn from '../../components/SelectColumn.vue'
  import type CaseFold from './CaseFold'

	const props = defineProps<{
		task: CaseFold
	}>()

</script>

<template>
  <form>
    <SelectColumn v-model="props.task.config.column" :schema="task.source?.schema" :type="Type.Utf8">
      What column do you want to convert?
    </SelectColumn>
  </form>
</template>
