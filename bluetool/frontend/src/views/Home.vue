<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <el-icon size="48" color="#409EFF"><Document /></el-icon>
          BlueTool
        </h1>
        <p class="hero-subtitle">AI 自动化测试用例生成工具</p>
        <p class="hero-description">
          把人工软件测试的完整思路，通过 AI 自动化复现<br>
          从「需求文档」一键生成「专业测试点 + 标准测试用例」
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/upload')">
            <el-icon><Upload /></el-icon> 开始上传文档
          </el-button>
          <el-button size="large" @click="$router.push('/history')">
            <el-icon><Clock /></el-icon> 查看历史记录
          </el-button>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#409EFF"><UploadFilled /></el-icon>
            <h3>需求文档上传</h3>
            <p>支持 Markdown、Word、PDF 等多种格式文档上传与解析</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#67C23A"><DocumentCopy /></el-icon>
            <h3>智能文档拆分</h3>
            <p>自动识别大文档，按功能模块、业务规则智能拆分</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#E6A23C"><Cpu /></el-icon>
            <h3>AI 测试点分析</h3>
            <p>调用大模型自动提取功能点、交互点、异常点、边界点</p>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="24" style="margin-top: 24px;">
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#F56C6C"><Edit /></el-icon>
            <h3>测试点编辑</h3>
            <p>可视化编辑界面，支持新增、删除、修改测试点</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#909399"><DocumentChecked /></el-icon>
            <h3>标准用例生成</h3>
            <p>基于测试点自动生成包含完整字段的标准测试用例</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card" shadow="hover">
            <el-icon size="48" color="#409EFF"><Download /></el-icon>
            <h3>结果导出</h3>
            <p>支持复制、导出为 JSON、Markdown 等多种格式</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="workflow-section">
      <h2 class="section-title">工作流程</h2>
      <el-steps :active="6" finish-status="success" align-center>
        <el-step title="需求可测性分析" description="分析需求文档的可测试性" />
        <el-step title="需求评审" description="AI 进行需求反讲" />
        <el-step title="提取测试点" description="自动提取各类测试点" />
        <el-step title="编写测试用例" description="生成标准格式用例" />
        <el-step title="评估测试范围" description="评估测试工作流" />
        <el-step title="准备测试资源" description="准备测试所需资源" />
      </el-steps>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.hero-section {
  background: white;
  border-radius: 16px;
  padding: 60px;
  text-align: center;
  margin-bottom: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.hero-title {
  font-size: 48px;
  color: #303133;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.hero-subtitle {
  font-size: 24px;
  color: #409EFF;
  margin-bottom: 20px;
  font-weight: 500;
}

.hero-description {
  font-size: 16px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.features-section {
  margin-bottom: 40px;
}

.section-title {
  text-align: center;
  font-size: 28px;
  color: #303133;
  margin-bottom: 32px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  height: 100%;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  font-size: 18px;
  color: #303133;
  margin: 16px 0 12px;
}

.feature-card p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.workflow-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>
