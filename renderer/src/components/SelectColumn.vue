<script setup lang="ts">

	import type { Field, Schema } from '@apache-arrow/esnext-cjs'

	const props = defineProps<{
		modelValue: string,
		schema: Schema,
		type?: number | number[],
	}>()

	const emit = defineEmits<{
		(event: 'update:modelValue', value: string): void
	}>()

	function isValidType(field: Field): boolean {
		if (props.type == null) {
			return true
		}
		if (Array.isArray(props.type)) {
			return props.type.includes(field.typeId)
		}
		return field.typeId === props.type
	}

	function onInput(event: Event) {
		emit('update:modelValue', (event.target as HTMLSelectElement).value)
	}

</script>

<template>
  <label>
    <slot/>
		<select :modelValue="modelValue" @input="onInput">
      <option></option>
      <option
        v-for="field in schema?.fields"
        :value="field.name"
        :disabled="!isValidType(field)"
      >{{ field.name }}</option>
    </select>
  </label>
</template>
