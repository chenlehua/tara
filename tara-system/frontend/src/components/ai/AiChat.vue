<template>
  <div class="ai-chat-container">
    <!-- 悬浮按钮 -->
    <div
      v-if="!isOpen"
      class="chat-fab"
      @click="toggleChat"
    >
      <el-icon :size="24"><ChatDotRound /></el-icon>
    </div>

    <!-- 对话窗口 -->
    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">
        <!-- 头部 -->
        <div class="chat-header">
          <div class="header-left">
            <el-icon :size="20"><ChatDotRound /></el-icon>
            <span class="header-title">TARA AI 助手</span>
          </div>
          <div class="header-actions">
            <el-button
              type="text"
              :icon="RefreshRight"
              @click="clearHistory"
              title="清空对话"
            />
            <el-button
              type="text"
              :icon="Close"
              @click="toggleChat"
              title="关闭"
            />
          </div>
        </div>

        <!-- 消息列表 -->
        <div ref="messageListRef" class="chat-messages">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">
              <el-icon :size="48"><ChatDotRound /></el-icon>
            </div>
            <h3>您好！我是 TARA AI 助手</h3>
            <p>我可以帮助您：</p>
            <ul>
              <li>分析汽车网络安全威胁</li>
              <li>解释 STRIDE 威胁模型</li>
              <li>推荐安全控制措施</li>
              <li>解答 ISO/SAE 21434 相关问题</li>
            </ul>
            <div class="quick-questions">
              <p>快速提问：</p>
              <el-tag
                v-for="q in quickQuestions"
                :key="q"
                class="quick-tag"
                @click="sendQuickQuestion(q)"
              >
                {{ q }}
              </el-tag>
            </div>
          </div>

          <!-- 消息列表 -->
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              <el-avatar v-if="msg.role === 'user'" :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar v-else :size="32" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><MagicStick /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-bubble" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="isLoading" class="message assistant">
            <div class="message-avatar">
              <el-avatar :size="32" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><MagicStick /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-bubble loading">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            placeholder="输入您的问题..."
            @keydown.enter.prevent="handleEnter"
            :disabled="isLoading"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            :loading="isLoading"
            :disabled="!inputMessage.trim()"
            @click="sendMessage"
          >
            发送
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import {
  ChatDotRound,
  Close,
  RefreshRight,
  User,
  MagicStick,
  Promotion,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chatApi } from '@/api/chat'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const props = defineProps<{
  projectId?: number
}>()

const isOpen = ref(false)
const isLoading = ref(false)
const inputMessage = ref('')
const messages = ref<Message[]>([])
const messageListRef = ref<HTMLElement>()

const quickQuestions = [
  'CAN总线有哪些安全威胁？',
  '什么是STRIDE威胁模型？',
  '如何评估攻击可行性？',
]

// 切换对话框
const toggleChat = () => {
  isOpen.value = !isOpen.value
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date(),
  })

  scrollToBottom()
  isLoading.value = true

  try {
    const response = await chatApi.sendMessage({
      message: userMessage,
      project_id: props.projectId,
      stream: false,
    })

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: response.data.message || response.data.content,
      timestamp: new Date(),
    })
  } catch (error: any) {
    console.error('Chat error:', error)
    
    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我暂时无法回答您的问题。请稍后再试。',
      timestamp: new Date(),
    })
    
    ElMessage.error('发送失败，请检查网络连接')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 发送快速问题
const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

// 处理回车键
const handleEnter = (e: KeyboardEvent) => {
  if (e.shiftKey) {
    // Shift+Enter 换行
    return
  }
  sendMessage()
}

// 清空历史
const clearHistory = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

// 格式化消息 (支持Markdown)
const formatMessage = (content: string): string => {
  try {
    const html = marked.parse(content) as string
    return DOMPurify.sanitize(html)
  } catch {
    return content
  }
}

// 格式化时间
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 监听消息变化
watch(
  () => messages.value.length,
  () => {
    scrollToBottom()
  }
)

// 存储/恢复对话历史
onMounted(() => {
  const saved = localStorage.getItem('tara-chat-history')
  if (saved) {
    try {
      const history = JSON.parse(saved)
      messages.value = history.map((m: any) => ({
        ...m,
        timestamp: new Date(m.timestamp),
      }))
    } catch {}
  }
})

watch(
  messages,
  (newMessages) => {
    localStorage.setItem('tara-chat-history', JSON.stringify(newMessages))
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
.ai-chat-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.chat-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  }
}

.chat-window {
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .header-title {
    font-size: 16px;
    font-weight: 600;
  }

  .header-actions {
    display: flex;
    gap: 4px;

    :deep(.el-button) {
      color: white;
      padding: 4px;

      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.welcome-message {
  text-align: center;
  color: #606266;
  padding: 24px;

  .welcome-icon {
    color: #667eea;
    margin-bottom: 16px;
  }

  h3 {
    margin: 0 0 12px;
    color: #303133;
  }

  ul {
    text-align: left;
    padding-left: 24px;
    margin: 12px 0;
  }

  li {
    margin: 8px 0;
  }

  .quick-questions {
    margin-top: 24px;

    p {
      margin-bottom: 12px;
      font-size: 13px;
    }
  }

  .quick-tag {
    margin: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #667eea;
      color: white;
      border-color: #667eea;
    }
  }
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;

  &.user {
    flex-direction: row-reverse;

    .message-bubble {
      background: #667eea;
      color: white;
      border-radius: 16px 16px 4px 16px;
    }

    .message-time {
      text-align: right;
    }
  }

  &.assistant {
    .message-bubble {
      background: white;
      color: #303133;
      border-radius: 16px 16px 16px 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
  }
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 75%;
}

.message-bubble {
  padding: 12px 16px;
  line-height: 1.6;
  word-break: break-word;

  :deep(p) {
    margin: 0 0 8px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
  }

  :deep(code) {
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
  }

  :deep(pre) {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;

    code {
      background: none;
      padding: 0;
    }
  }

  &.loading {
    display: flex;
    gap: 4px;
    padding: 16px;

    .dot {
      width: 8px;
      height: 8px;
      background: #667eea;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;

      &:nth-child(1) {
        animation-delay: -0.32s;
      }

      &:nth-child(2) {
        animation-delay: -0.16s;
      }
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  background: white;

  :deep(.el-textarea__inner) {
    resize: none;
    border-radius: 12px;
  }

  .el-button {
    flex-shrink: 0;
    align-self: flex-end;
    border-radius: 12px;
  }
}

// 动画
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

// 响应式
@media (max-width: 480px) {
  .chat-window {
    width: calc(100vw - 32px);
    height: calc(100vh - 100px);
    position: fixed;
    bottom: 16px;
    right: 16px;
  }
}
</style>
