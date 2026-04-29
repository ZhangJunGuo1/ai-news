<template>
  <div class="llm-chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">🤖</div>
        <h3>AI 新闻助手</h3>
        <p>我是一名专业的新闻从业者，可以帮您：</p>
        <ul>
          <li>撰写新闻稿件</li>
          <li>分析新闻热点</li>
          <li>编辑和润色文章</li>
          <li>生成新闻摘要</li>
        </ul>
        <p>请在下方输入您的问题或需求</p>
      </div>
      
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message"
        :class="msg.role"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-wrapper">
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
          </div>
          <div v-if="msg.role === 'assistant'" class="message-actions">
            <el-button size="small" type="primary" @click="copyMessage(msg.content)">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button size="small" type="primary" @click="regenerateMessage(index)" :loading="isRegenerating">
              <el-icon><RefreshRight /></el-icon>
              重新生成
            </el-button>
            <el-button size="small" type="primary" @click="collectMessage(msg.content)">
              <el-icon><Download /></el-icon>
              采集新闻
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="input-wrapper">
        <textarea
          v-model="inputMessage"
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="输入您的问题或需求..."
          rows="1"
          ref="textareaRef"
        ></textarea>
        <el-button 
          type="primary" 
          @click="sendMessage" 
          :loading="isLoading"
          :disabled="!inputMessage.trim()"
          class="send-button"
        >
          发送
        </el-button>
      </div>
      <div class="input-hint">按 Enter 发送，Shift + Enter 换行</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { CopyDocument, RefreshRight, Download } from '@element-plus/icons-vue'
import { post } from '../utils/request'
import { useMessage } from '../composables/useMessage'

const $message = useMessage()

const messages = ref<Array<{role: string, content: string}>>([])
const inputMessage = ref('')
const isLoading = ref(false)
const isRegenerating = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatMessage = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const autoResizeTextarea = () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 150) + 'px'
    }
  })
}

watch(inputMessage, autoResizeTextarea)

const sendMessage = async () => {
  const userMessage = inputMessage.value.trim()
  if (!userMessage || isLoading.value) return

  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const conversationHistory = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const data: any = await post('/api/llm-chat', {
      messages: conversationHistory
    })

    if (data.success) {
      messages.value.push({ role: 'assistant', content: data.content })
    } else {
      $message.error(data.message || 'AI 回复失败')
    }
  } catch (error: any) {
    $message.error(error.message || '请求失败，请检查网络连接')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
const resetChat = () => {
  messages.value = []
  inputMessage.value = ''
}

const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    $message.success('已复制到剪贴板')
  } catch {
    $message.error('复制失败')
  }
}

const regenerateMessage = async (index: number) => {
  if (isRegenerating.value || isLoading.value) return
  
  const lastUserMessage = [...messages.value.slice(0, index)].reverse().find(m => m.role === 'user')
  if (!lastUserMessage) {
    $message.warning('没有可重新生成的消息')
    return
  }

  messages.value.splice(index, 1)
  isRegenerating.value = true
  isLoading.value = true
  scrollToBottom()

  try {
    const conversationHistory = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const data: any = await post('/api/llm-chat', {
      messages: conversationHistory
    })

    if (data.success) {
      messages.value.push({ role: 'assistant', content: data.content })
    } else {
      $message.error(data.message || 'AI 回复失败')
    }
  } catch (error: any) {
    $message.error(error.message || '请求失败，请检查网络连接')
  } finally {
    isRegenerating.value = false
    isLoading.value = false
    scrollToBottom()
  }
}

const collectMessage = async (content: string) => {
  try {
    const data: any = await post('/api/collect-news', {
      source: 'llm',
      content: content
    })

    if (data.success) {
      $message.success(data.message || '新闻已采集到草稿箱')
    } else {
      $message.error(data.message || '采集失败')
    }
  } catch (error: any) {
    $message.error(error.message || '采集失败')
  }
}

defineExpose({ resetChat })
</script>

<style scoped>
.llm-chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-large);
  overflow: hidden;
  background: var(--bg-card);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: var(--text-primary);
}

.welcome-message p {
  margin: 8px 0;
}

.welcome-message ul {
  text-align: left;
  display: inline-block;
  margin: 12px 0;
  padding-left: 20px;
}

.welcome-message li {
  margin: 6px 0;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.message-actions {
  display: flex;
  gap: 8px;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: var(--bg-container);
  flex-shrink: 0;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.message.user .message-content {
  background: var(--primary-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: var(--bg-container);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-text {
  word-wrap: break-word;
  white-space: pre-wrap;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-4px);
  }
}

.chat-input-area {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-card);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  background: var(--bg-container);
  color: var(--text-primary);
  max-height: 150px;
  overflow-y: auto;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.send-button {
  height: 44px;
  min-width: 80px;
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
}

@media (max-width: 768px) {
  .llm-chat-container {
    height: 500px;
  }

  .message {
    max-width: 95%;
  }
}
</style>
