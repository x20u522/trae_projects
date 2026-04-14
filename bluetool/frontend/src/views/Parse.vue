<template>
  <div class="parse-container">
    <el-card v-loading="loading" element-loading-text="正在解析文档...">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><DocumentCopy /></el-icon>
            文档解析预览
          </h2>
          <el-button type="primary" @click="generateTestPoints" :loading="generating">
            <el-icon><Cpu /></el-icon> AI 生成测试点
          </el-button>
        </div>
      </template>

      <div v-if="error" class="error-message">
        <el-alert :title="error" type="error" show-icon />
      </div>

      <!-- 文档元数据 -->
      <div v-if="metadata" class="metadata-section">
        <h3 class="section-title">文档元数据</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card body-style="{ padding: '12px' }">
              <div class="meta-item">
                <span class="meta-label">文档类型</span>
                <span class="meta-value">{{ metadata.type || '-' }}</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card body-style="{ padding: '12px' }">
              <div class="meta-item">
                <span class="meta-label">段落数</span>
                <span class="meta-value">{{ metadata.paragraph_count || '-' }}</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card body-style="{ padding: '12px' }">
              <div class="meta-item">
                <span class="meta-label">表格数</span>
                <span class="meta-value">{{ metadata.table_count || '-' }}</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card body-style="{ padding: '12px' }">
              <div class="meta-item">
                <span class="meta-label">图片数</span>
                <span class="meta-value">{{ metadata.image_count || '-' }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 表格信息 -->
      <div v-if="tables.length > 0" class="tables-section">
        <h3 class="section-title">识别到的表格</h3>
        <el-table :data="tables" border style="width: 100%">
          <el-table-column prop="index" label="序号" width="80" />
          <el-table-column prop="summary" label="表格摘要" />
          <el-table-column prop="row_count" label="行数" width="80" />
          <el-table-column prop="col_count" label="列数" width="80" />
          <el-table-column label="表头" width="300">
            <template #default="scope">
              <span v-if="scope.row.headers?.length">{{ scope.row.headers.join(', ') }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 图片信息 -->
      <div v-if="images.length > 0" class="images-section">
        <h3 class="section-title">识别到的图片</h3>
        <el-table :data="images" border style="width: 100%">
          <el-table-column prop="index" label="序号" width="80" />
          <el-table-column prop="description" label="图片描述" />
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="page" label="所在页码" width="120" />
        </el-table>
      </div>

      <div v-if="chunks.length > 0" class="chunks-section">
        <h3 class="section-title">文档拆分结果</h3>
        <el-collapse v-model="activeChunks">
          <el-collapse-item
            v-for="(chunk, index) in chunks"
            :key="index"
            :title="chunk.title || `模块 ${index + 1}`"
            :name="index"
          >
            <div class="chunk-content">
              <el-tag size="small" :type="getChunkType(chunk.type)">
                {{ chunk.type || '内容' }}
              </el-tag>
              <pre class="content-preview">{{ chunk.content }}</pre>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div v-if="fullContent" class="full-content-section">
        <h3 class="section-title">完整内容</h3>
        <el-input
          v-model="fullContent"
          type="textarea"
          :rows="10"
          readonly
          class="full-content-textarea"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  fileId: String
})

const router = useRouter()
const loading = ref(false)
const generating = ref(false)
const error = ref('')
const chunks = ref([])
const fullContent = ref('')
const tables = ref([])
const images = ref([])
const metadata = ref({})
const activeChunks = ref([0])

onMounted(() => {
  if (props.fileId) {
    parseDocument()
  }
})

const parseDocument = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post('/api/parse', {
      file_id: props.fileId
    })

    if (response.data.success) {
      chunks.value = response.data.chunks || []
      fullContent.value = response.data.content || ''
      tables.value = response.data.tables || []
      images.value = response.data.images || []
      metadata.value = response.data.metadata || {}

      localStorage.setItem('currentChunks', JSON.stringify(chunks.value))
      localStorage.setItem('currentContent', fullContent.value)
      localStorage.setItem('currentTables', JSON.stringify(tables.value))
      localStorage.setItem('currentImages', JSON.stringify(images.value))

      ElMessage.success('文档解析成功')
    } else {
      error.value = response.data.error || '解析失败'
      ElMessage.error(error.value)
    }
  } catch (err) {
    error.value = '解析失败: ' + (err.response?.data?.error || err.message)
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const generateTestPoints = async () => {
  if (chunks.value.length === 0) {
    ElMessage.warning('请先解析文档')
    return
  }

  generating.value = true

  try {
    const response = await axios.post('/api/generate-test-points', {
      chunks: chunks.value,
      tables: tables.value,
      images: images.value,
      model: 'gpt-3.5-turbo'
    })

    if (response.data.test_points) {
      localStorage.setItem('currentTestPoints', JSON.stringify(response.data.test_points))
      ElMessage.success(`成功生成 ${response.data.test_points.length} 个测试点`)
      router.push('/test-points')
    } else {
      ElMessage.error(response.data.error || '生成测试点失败')
    }
  } catch (err) {
    ElMessage.error('生成测试点失败: ' + (err.response?.data?.error || err.message))
  } finally {
    generating.value = false
  }
}

const getChunkType = (type) => {
  const typeMap = {
    'overview': 'success',
    'section': 'primary',
    'content': 'info'
  }
  return typeMap[type] || 'info'
}
</script>

<style scoped>
.parse-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #303133;
}

.error-message {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  color: #303133;
  margin: 20px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.metadata-section {
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.meta-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.tables-section,
.images-section {
  margin-bottom: 20px;
}

.chunks-section {
  margin-bottom: 24px;
}

.chunk-content {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.content-preview {
  margin: 12px 0 0;
  padding: 12px;
  background: white;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.full-content-textarea :deep(.el-textarea__inner) {
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
