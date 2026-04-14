<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><UploadFilled /></el-icon>
            上传需求文档
          </h2>
          <p class="subtitle">支持 Markdown、Word、PDF 格式</p>
        </div>
      </template>

      <el-upload
        class="upload-area"
        drag
        action="/api/upload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-progress="handleProgress"
        :before-upload="beforeUpload"
        accept=".md,.docx,.pdf,.txt"
      >
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="upload-text">
          <p>拖拽文件到此处，或 <em>点击上传</em></p>
          <p class="upload-hint">支持格式：.md, .docx, .pdf, .txt</p>
          <p class="upload-hint">文件大小不超过 100MB</p>
        </div>
      </el-upload>

      <el-progress
        v-if="uploadProgress > 0 && uploadProgress < 100"
        :percentage="uploadProgress"
        :stroke-width="8"
        status="success"
        class="upload-progress"
      />

      <div v-if="uploadedFile" class="upload-result">
        <el-alert
          :title="`上传成功: ${uploadedFile.original_name}`"
          type="success"
          show-icon
          :closable="false"
        />
        <div class="action-buttons">
          <el-button type="primary" @click="goToParse">
            <el-icon><Document /></el-icon> 开始解析文档
          </el-button>
          <el-button @click="resetUpload">
            <el-icon><RefreshRight /></el-icon> 重新上传
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="recent-files-card" v-if="recentFiles.length > 0">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Clock /></el-icon>
            最近上传
          </h3>
        </div>
      </template>
      <el-table :data="recentFiles" style="width: 100%">
        <el-table-column prop="original_name" label="文件名" min-width="200" />
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="continueParse(scope.row)">
              继续解析
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const uploadProgress = ref(0)
const uploadedFile = ref(null)
const recentFiles = ref([])

onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  try {
    const response = await axios.get('/api/history')
    if (response.data.success) {
      recentFiles.value = response.data.history.slice(-5).reverse()
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

const beforeUpload = (file) => {
  const allowedTypes = ['md', 'docx', 'pdf', 'txt']
  const extension = file.name.split('.').pop().toLowerCase()

  if (!allowedTypes.includes(extension)) {
    ElMessage.error('请上传Markdown、Word、PDF、txt格式文件')
    return false
  }

  if (file.size > 100 * 1024 * 1024) {
    ElMessage.error('文件大小超出限制（最大100MB）')
    return false
  }

  return true
}

const handleProgress = (event) => {
  uploadProgress.value = Math.round(event.percent)
}

const handleSuccess = (response) => {
  uploadProgress.value = 100
  if (response.success) {
    uploadedFile.value = response.file
    ElMessage.success('文件上传成功')
    loadHistory()
  } else {
    ElMessage.error(response.error || '上传失败')
  }
}

const handleError = () => {
  uploadProgress.value = 0
  ElMessage.error('上传失败，请重试')
}

const resetUpload = () => {
  uploadedFile.value = null
  uploadProgress.value = 0
}

const goToParse = () => {
  if (uploadedFile.value) {
    router.push(`/parse/${uploadedFile.value.id}`)
  }
}

const continueParse = (file) => {
  router.push(`/parse/${file.id}`)
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 24px;
}

.card-header {
  text-align: center;
}

.card-header h2, .card-header h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  margin: 8px 0 0;
  font-size: 14px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f5f7fa;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
}

.upload-text p {
  margin: 8px 0;
  color: #606266;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
  cursor: pointer;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin-top: 20px;
}

.upload-result {
  margin-top: 24px;
  text-align: center;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.recent-files-card {
  margin-top: 24px;
}
</style>
