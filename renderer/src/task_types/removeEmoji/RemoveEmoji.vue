<script setup lang="ts">

	import type { RemoveEmojiConfig } from './index'
  import { Schema, Type } from '@apache-arrow/esnext-cjs'
	import SelectColumn from '../../components/SelectColumn.vue'

	const props = defineProps<{
		config: RemoveEmojiConfig
	}>()

	const emit = defineEmits<{
		(event: 'update:config', config: RemoveEmojiConfig): void
	}>()

  let schema = new Schema()

</script>

<template>
	<form>
    <p>
      <SelectColumn v-model="config.column" :schema="schema" :type="Type.Utf8">What column do you want to remove emoji from?</SelectColumn>
    </p>

    <label><input type="radio" name="cc" value="name" v-model="config.mode"> Replace the emoji with a descriptive label</label>
    <label><input type="radio" name="cc" value="string" v-model="config.mode"> Replace the emoji with a string of my choosing</label>
    <label><input type="radio" name="cc" value="remove" v-model="config.mode"> Remove the emoji entirely</label>

    <p v-if="config.mode == 'string'">
      <label>Replacement string</label>
      <input type="text" v-model="config.replacement">
    </p>
	</form>
</template>

<style scoped>

  label {
    display: block;
  }

</style>
