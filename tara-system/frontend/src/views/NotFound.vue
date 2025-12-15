<template>
  <div class="not-found-container animate-fadeIn">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在或已被移除。</p>
      <router-link to="/" class="tara-btn tara-btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
          <path d="M9 22V12h6v10"/>
        </svg>
        返回工作台
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--brand-blue), var(--brand-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  margin-bottom: 16px;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
}

p {
  font-size: 16px;
  color: var(--text-muted);
  margin-bottom: 32px;
}
</style>
