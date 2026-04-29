<template>
  <router-view />
</template>

<script setup lang="ts">
// App.vue - 应用根组件
</script>

<style>
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --background-color: #1e293b;
  --card-background: #0f172a;
  --border-color: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  --border-radius: 8px;
  --transition-speed: 0.3s;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--background-color);
}

a {
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-speed) ease;
}

a:hover {
  color: #60a5fa;
  text-decoration: underline;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--background-color);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--secondary-color);
}

/* 选择文本样式 */
::selection {
  background: rgba(59, 130, 246, 0.3);
  color: var(--text-primary);
}

/* 通用动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 通用类 */
.fade-in {
  animation: fadeIn 0.3s ease;
}

.slide-in {
  animation: slideIn 0.3s ease;
}

/* 响应式断点 */
@media (max-width: 768px) {
  :root {
    --border-radius: 6px;
  }
}
</style>