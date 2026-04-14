<template>
  <div class="app-container">
    <el-container>
      <el-header class="header">
        <div class="logo">
          <el-icon size="32" color="#409EFF"><Document /></el-icon>
          <span class="title">BlueTool</span>
          <span class="subtitle">AI 自动化测试用例生成工具</span>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <el-icon><HomeFilled /></el-icon> 首页
          </router-link>
          <router-link to="/upload" class="nav-link" :class="{ active: $route.path === '/upload' }">
            <el-icon><UploadFilled /></el-icon> 文档上传
          </router-link>
          <router-link to="/test-points" class="nav-link" :class="{ active: $route.path === '/test-points' }">
            <el-icon><List /></el-icon> 测试点
          </router-link>
          <router-link to="/test-cases" class="nav-link" :class="{ active: $route.path === '/test-cases' }">
            <el-icon><DocumentChecked /></el-icon> 测试用例
          </router-link>
          <router-link to="/history" class="nav-link" :class="{ active: $route.path === '/history' }">
            <el-icon><Clock /></el-icon> 历史记录
          </router-link>
        </nav>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
      <el-footer class="footer">
        <p>BlueTool © 2026 - AI 自动化测试用例生成工具</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin-left: 10px;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  color: #606266;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
  font-size: 14px;
}

.nav-link:hover {
  background: #ecf5ff;
  color: #409EFF;
}

.nav-link.active {
  background: #409EFF;
  color: white;
}

.main-content {
  padding: 30px 40px;
  min-height: calc(100vh - 140px);
}

.footer {
  background: rgba(255, 255, 255, 0.9);
  text-align: center;
  color: #666;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
