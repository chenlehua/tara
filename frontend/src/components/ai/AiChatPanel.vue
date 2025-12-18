<template>
  <aside class="ai-panel">
    <div class="ai-header">
      <div class="ai-info">
        <div class="ai-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96.44 2.5 2.5 0 01-2.96-3.08 3 3 0 01-.34-5.58 2.5 2.5 0 011.32-4.24 2.5 2.5 0 011.98-3A2.5 2.5 0 019.5 2z"/>
            <path d="M14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.96.44 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-1.98-3A2.5 2.5 0 0014.5 2z"/>
          </svg>
        </div>
        <div>
          <div class="ai-title">TARA AI 助手</div>
          <div class="ai-status">
            <span class="dot"></span>
            Qwen3-235B · 在线
          </div>
        </div>
      </div>
      <div class="ai-header-actions">
        <button class="btn-icon btn-ghost" @click="clearMessages">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
        <button class="btn-icon btn-ghost" @click="$emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="ai-mode-tabs">
      <button 
        class="mode-tab" 
        :class="{ active: currentMode === 'chat' }"
        @click="currentMode = 'chat'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        </svg>
        智能对话
      </button>
      <button 
        class="mode-tab" 
        :class="{ active: currentMode === 'optimize' }"
        @click="currentMode = 'optimize'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
        报告优化
      </button>
    </div>

    <div class="ai-quick-actions">
      <div class="quick-actions-grid">
        <button 
          v-for="action in quickActions" 
          :key="action.label"
          class="quick-action-btn"
          @click="sendQuickAction(action.prompt)"
        >
          <div class="quick-action-icon" :style="{ background: action.bgColor, color: action.color }">
            <component :is="action.icon" />
          </div>
          <div>
            <div class="quick-action-label">{{ action.label }}</div>
            <div class="quick-action-desc">{{ action.desc }}</div>
          </div>
        </button>
      </div>
    </div>

    <div class="ai-messages" ref="messagesContainer">
      <template v-for="(msg, index) in messages" :key="index">
        <!-- Assistant Message -->
        <div v-if="msg.role === 'assistant'" class="message assistant animate-fadeIn">
          <div class="message-header">
            <div class="message-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
              </svg>
            </div>
            <span class="message-time">AI · {{ msg.time }}</span>
          </div>
          <div class="message-bubble" v-html="formatMessage(msg.content)"></div>
          <div v-if="msg.sources?.length" class="message-sources">
            <span>参考：</span>
            <span 
              v-for="source in msg.sources" 
              :key="source" 
              class="source-tag"
            >
              {{ source }}
            </span>
          </div>
        </div>

        <!-- User Message -->
        <div v-else class="message user animate-fadeIn">
          <div class="message-bubble">{{ msg.content }}</div>
          <div class="user-time">{{ msg.time }}</div>
        </div>
      </template>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="typing-indicator">
        <div class="message-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5">
            <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
          </svg>
        </div>
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <div class="ai-input">
      <div class="input-container" :class="{ focused: inputFocused }">
        <textarea
          ref="inputRef"
          v-model="inputMessage"
          rows="2"
          placeholder="输入您的问题或修改意见..."
          @keydown="handleKeyDown"
          @focus="inputFocused = true"
          @blur="inputFocused = false"
        ></textarea>
        <div class="input-toolbar">
          <div class="input-tools">
            <button class="tool-btn" title="附件">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
              </svg>
            </button>
            <button class="tool-btn" title="图片">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
            </button>
            <button class="tool-btn" title="语音">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
                <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"/>
              </svg>
            </button>
          </div>
          <button class="send-btn" @click="sendMessage" :disabled="!inputMessage.trim()">
            发送
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="input-hint">
        <span>Enter 发送 · Shift+Enter 换行</span>
        <span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          深度推理
        </span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { chatApi } from '@/api/chat'

// Emits
defineEmits(['close'])

// Icons
const IconTarget = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`
}
const IconPath = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M6 21V9a9 9 0 009 9"/></svg>`
}
const IconActivity = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
}
const IconShield = {
  template: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`
}

// Types
interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
  sources?: string[]
}

// State
const currentMode = ref<'chat' | 'optimize'>('chat')
const messages = ref<Message[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const inputFocused = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

// Quick actions
const quickActions = [
  {
    label: '威胁识别',
    desc: 'STRIDE分析',
    prompt: '请对当前项目进行STRIDE威胁识别分析',
    icon: IconTarget,
    bgColor: 'rgba(59,130,246,0.12)',
    color: '#60A5FA'
  },
  {
    label: '攻击路径',
    desc: '图谱推理',
    prompt: '请分析可能的攻击路径并生成攻击树',
    icon: IconPath,
    bgColor: 'rgba(139,92,246,0.12)',
    color: '#A78BFA'
  },
  {
    label: '风险计算',
    desc: 'CAL评估',
    prompt: '请计算各威胁的CAL风险等级',
    icon: IconActivity,
    bgColor: 'rgba(245,158,11,0.12)',
    color: '#FBBF24'
  },
  {
    label: '措施推荐',
    desc: '策略匹配',
    prompt: '请根据威胁分析结果推荐相应的安全措施',
    icon: IconShield,
    bgColor: 'rgba(16,185,129,0.12)',
    color: '#34D399'
  }
]

// Methods
const getTime = () => {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const addMessage = (msg: Message) => {
  messages.value.push(msg)
  scrollToBottom()
}

const sendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content) return

  addMessage({
    role: 'user',
    content,
    time: getTime()
  })

  inputMessage.value = ''
  isTyping.value = true

  try {
    // 调用API
    const response = await chatApi.sendMessage(content)
    isTyping.value = false
    
    addMessage({
      role: 'assistant',
      content: response.content || generateMockResponse(content),
      time: getTime(),
      sources: response.sources || ['ISO 21434']
    })
  } catch (error) {
    isTyping.value = false
    // 使用模拟响应
    setTimeout(() => {
      addMessage({
        role: 'assistant',
        content: generateMockResponse(content),
        time: getTime(),
        sources: ['ISO 21434', 'STRIDE']
      })
    }, 1000)
  }
}

const generateMockResponse = (content: string) => {
  if (content.includes('威胁') || content.includes('STRIDE')) {
    return `根据STRIDE威胁模型，我已对您的请求进行了分析：\n\n**威胁识别结果**\n• **Spoofing (伪造)**: 检测到CAN总线消息伪造风险\n• **Tampering (篡改)**: ECU固件可能被恶意修改\n• **Information Disclosure (信息泄露)**: 诊断接口可能泄露敏感数据\n\n如需详细分析，请继续提问。`
  }
  if (content.includes('风险') || content.includes('CAL')) {
    return `**风险评估结果**\n\n已完成CAL等级评估：\n• **CAL-4 (极高风险)**: 3项\n• **CAL-3 (高风险)**: 8项\n• **CAL-2 (中风险)**: 15项\n• **CAL-1 (低风险)**: 23项\n\n建议优先处理CAL-4级别的风险项。`
  }
  if (content.includes('措施') || content.includes('安全')) {
    return `**安全措施推荐**\n\n针对已识别的威胁，建议采取以下措施：\n\n1. **消息认证 (SecOC)** - 防止CAN总线消息伪造\n2. **安全启动** - 验证ECU固件完整性\n3. **访问控制** - 限制诊断接口访问权限\n4. **加密通信** - 保护敏感数据传输\n\n如需具体实施方案，请告诉我。`
  }
  return `根据您的问题，我进行了分析：\n\n**分析结果**\n您的问题涉及TARA分析流程，建议参考ISO 21434第8章进行系统性的威胁分析和风险评估。\n\n如需进一步分析，请继续提问。`
}

const sendQuickAction = (prompt: string) => {
  inputMessage.value = prompt
  sendMessage()
}

const clearMessages = () => {
  messages.value = []
  initializeMessages()
}

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const initializeMessages = () => {
  addMessage({
    role: 'assistant',
    content: '您好！我是TARA智能分析助手，基于Qwen3大模型。\n\n我可以帮您：\n• **生成报告** - 上传文件后一键生成TARA报告\n• **优化内容** - 多轮对话逐步完善报告\n• **回答问题** - 解答安全分析相关疑问\n\n请开始使用吧！',
    time: getTime(),
    sources: ['ISO 21434', 'UN R155']
  })
}

onMounted(() => {
  initializeMessages()
})
</script>

<style scoped>
.ai-panel {
  width: 420px;
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(24px);
  border-left: 1px solid var(--border-color);
  transition: width var(--transition-slow), opacity var(--transition-slow);
  position: relative;
  z-index: 15;
}

.ai-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.ai-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-pink) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.ai-avatar svg {
  width: 22px;
  height: 22px;
  color: white;
}

.ai-title {
  font-size: 15px;
  font-weight: 600;
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.ai-status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34D399;
  animation: pulse 2s infinite;
}

.ai-header-actions {
  display: flex;
  gap: 6px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-icon svg {
  width: 18px;
  height: 18px;
}

/* AI Mode Tabs */
.ai-mode-tabs {
  display: flex;
  padding: 14px 16px;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
}

.mode-tab {
  flex: 1;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.mode-tab:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mode-tab.active {
  background: rgba(59, 130, 246, 0.12);
  color: var(--brand-blue);
}

.mode-tab svg {
  width: 16px;
  height: 16px;
}

/* AI Quick Actions */
.ai-quick-actions {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: left;
}

.quick-action-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
}

.quick-action-btn:active {
  transform: translateY(0);
}

.quick-action-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-action-icon svg {
  width: 18px;
  height: 18px;
}

.quick-action-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-action-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* AI Messages */
.ai-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  max-width: 92%;
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--brand-purple), var(--brand-pink));
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar svg {
  width: 14px;
  height: 14px;
  color: white;
}

.message-time {
  font-size: 12px;
  color: var(--text-muted);
}

.message-bubble {
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  line-height: 1.7;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--brand-blue), #2563EB);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-bottom-left-radius: 4px;
}

.message-sources {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.message-sources > span:first-child {
  font-size: 11px;
  color: var(--text-disabled);
}

.source-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  background: var(--bg-hover);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.source-tag:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.user-time {
  text-align: right;
  font-size: 11px;
  color: var(--text-disabled);
  margin-top: 6px;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.typing-dots {
  display: flex;
  gap: 6px;
  padding: 14px 18px;
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: bounce 0.6s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

/* AI Input */
.ai-input {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.input-container {
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.input-container.focused {
  border-color: var(--border-focus);
}

.input-container textarea {
  width: 100%;
  padding: 14px 16px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
}

.input-container textarea::placeholder {
  color: var(--text-muted);
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-top: 1px solid var(--border-color);
}

.input-tools {
  display: flex;
  gap: 4px;
}

.tool-btn {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.tool-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.tool-btn svg {
  width: 16px;
  height: 16px;
}

.send-btn {
  padding: 8px 18px;
  border-radius: var(--radius-md);
  border: none;
  background: linear-gradient(135deg, var(--brand-blue), var(--brand-purple));
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-normal);
}

.send-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.02);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 16px;
  height: 16px;
}

.input-hint {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  padding: 0 4px;
  font-size: 11px;
  color: var(--text-disabled);
}

.input-hint span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.input-hint svg {
  width: 12px;
  height: 12px;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive */
@media (max-width: 1400px) {
  .ai-panel {
    display: none;
  }
}
</style>
