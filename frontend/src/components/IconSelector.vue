<template>
  <div class="icon-selector">
    <el-select
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :placeholder="placeholder"
      filterable
      :clearable="clearable"
      class="icon-select"
    >
      <template #prefix v-if="modelValue">
        <span class="selected-icon-preview">{{ getIconEmoji(modelValue) }}</span>
      </template>
      <el-option
        v-for="icon in ICON_LIST"
        :key="icon.name"
        :label="icon.label"
        :value="icon.name"
      >
        <div class="icon-option">
          <span class="icon-emoji">{{ icon.emoji }}</span>
          <span class="icon-label">{{ icon.label }}</span>
          <span class="icon-name">({{ icon.name }})</span>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { ICON_LIST, getIconByName } from '../config/icons'

interface Props {
  modelValue: string
  placeholder?: string
  clearable?: boolean
}

withDefaults(defineProps<Props>(), {
  placeholder: '请选择图标',
  clearable: true
})

defineEmits(['update:modelValue'])

const getIconEmoji = (name: string): string => {
  return getIconByName(name)
}
</script>

<style scoped>
.icon-selector {
  width: 100%;
}

.icon-select {
  width: 100%;
}

.selected-icon-preview {
  font-size: 18px;
  margin-right: 4px;
}

.icon-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.icon-emoji {
  font-size: 20px;
  width: 28px;
  text-align: center;
}

.icon-label {
  flex: 1;
  font-size: 14px;
}

.icon-name {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
