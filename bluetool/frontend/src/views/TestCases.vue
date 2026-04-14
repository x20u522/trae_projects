<template>
  <div class="test-cases-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><DocumentChecked /></el-icon>
            测试用例
            <el-tag v-if="testCases.length > 0" type="success">
              共 {{ testCases.length }} 条
            </el-tag>
          </h2>
          <div class="header-actions">
            <el-button @click="exportCases('json')">
              <el-icon><Document /></el-icon> 导出 JSON
            </el-button>
            <el-button @click="exportCases('markdown')">
              <el-icon><DocumentCopy /></el-icon> 导出 Markdown
            </el-button>
            <el-button type="success" @click="exportCases('excel')">
              <el-icon><Table /></el-icon> 导出 Excel
            </el-button>
            <el-button type="primary" @click="copyAllCases">
              <el-icon><CopyDocument /></el-icon> 复制全部
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="testCases.length === 0" class="empty-state">
        <el-empty description="暂无测试用例">
          <el-button type="primary" @click="$router.push('/test-points')">
            去生成测试用例
          </el-button>
        </el-empty>
      </div>

      <div v-else>
        <el-collapse v-model="activeCases">
          <el-collapse-item
            v-for="(testCase, index) in testCases"
            :key="index"
            :name="index"
          >
            <template #title>
              <div class="case-title">
                <span class="case-id">{{ testCase.case_id }}</span>
                <span class="case-name">{{ testCase.title }}</span>
                <el-tag size="small" :type="getPriorityType(testCase.priority)">
                  {{ testCase.priority }}
                </el-tag>
                <el-tag size="small" type="info" style="margin-left: 8px;">
                  {{ testCase.module }}
                </el-tag>
                <el-tag size="small" type="success" style="margin-left: 8px;">
                  {{ testCase.scene || '正向' }}
                </el-tag>
              </div>
            </template>

            <div class="case-detail">
              <div class="detail-section">
                <h4>基本信息</h4>
                <el-descriptions :column="2" size="small">
                  <el-descriptions-item label="所属模块">{{ testCase.module }}</el-descriptions-item>
                  <el-descriptions-item label="涉及端侧">{{ testCase.involve_side || 'Web端' }}</el-descriptions-item>
                  <el-descriptions-item label="场景">{{ testCase.scene || '正向' }}</el-descriptions-item>
                  <el-descriptions-item label="优先级">{{ testCase.priority }}</el-descriptions-item>
                </el-descriptions>
              </div>

              <div class="detail-section">
                <h4>前置条件</h4>
                <ol>
                  <li v-for="(pre, i) in testCase.preconditions" :key="i">{{ pre }}</li>
                </ol>
              </div>

              <div class="detail-section">
                <h4>测试步骤</h4>
                <el-table :data="formatSteps(testCase.steps)" border size="small">
                  <el-table-column type="index" label="步骤" width="60" align="center" />
                  <el-table-column prop="content" label="操作" />
                </el-table>
              </div>

              <div class="detail-section">
                <h4>预期结果</h4>
                <el-table :data="formatSteps(testCase.expected_results)" border size="small">
                  <el-table-column type="index" label="步骤" width="60" align="center" />
                  <el-table-column prop="content" label="预期" />
                </el-table>
              </div>

              <div class="detail-actions">
                <el-button link type="primary" @click="copyCase(testCase)">
                  <el-icon><CopyDocument /></el-icon> 复制此用例
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <el-dialog v-model="exportDialogVisible" title="导出结果" width="800px">
      <el-input
        v-model="exportContent"
        type="textarea"
        :rows="20"
        readonly
      />
      <template #footer>
        <el-button @click="exportDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadExport">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const testCases = ref([])
const activeCases = ref([0])
const exportDialogVisible = ref(false)
const exportContent = ref('')
const exportFormat = ref('json')

onMounted(() => {
  const saved = localStorage.getItem('currentTestCases')
  if (saved) {
    try {
      testCases.value = JSON.parse(saved)
    } catch (e) {
      console.error('解析测试用例失败:', e)
    }
  }
})

const getPriorityType = (priority) => {
  const map = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return map[priority] || 'info'
}

const formatSteps = (steps) => {
  if (!steps) return []
  if (typeof steps === 'string') {
    return steps.split('\n').filter(s => s.trim()).map(s => ({ content: s.trim() }))
  }
  if (Array.isArray(steps)) {
    return steps.map(s => ({ content: s }))
  }
  return []
}

const copyCase = (testCase) => {
  const content = formatCaseForCopy(testCase)
  navigator.clipboard.writeText(content).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const copyAllCases = () => {
  const content = testCases.value.map(formatCaseForCopy).join('\n\n' + '='.repeat(50) + '\n\n')
  navigator.clipboard.writeText(content).then(() => {
    ElMessage.success('全部用例已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const formatCaseForCopy = (testCase) => {
  let content = `【${testCase.case_id}】${testCase.title}\n`
  content += `模块: ${testCase.module}\n`
  content += `优先级: ${testCase.priority}\n\n`
  content += `前置条件:\n`
  testCase.preconditions?.forEach((pre, i) => {
    content += `${i + 1}. ${pre}\n`
  })
  content += `\n测试步骤:\n`
  const steps = formatSteps(testCase.steps)
  steps.forEach((step, i) => {
    content += `${i + 1}. ${step.content}\n`
  })
  content += `\n预期结果:\n`
  const results = formatSteps(testCase.expected_results)
  results.forEach((result, i) => {
    content += `${i + 1}. ${result.content}\n`
  })
  return content
}

const exportCases = async (format) => {
  if (testCases.value.length === 0) {
    ElMessage.warning('暂无测试用例可导出')
    return
  }

  try {
    const response = await axios.post('/api/export', {
      test_cases: testCases.value,
      format: format
    })

    if (response.data.success) {
      if (format === 'excel') {
        // Excel 导出直接下载
        const filename = response.data.data
        window.location.href = `/api/download-excel/${filename}`
        ElMessage.success('Excel文件导出成功')
      } else {
        exportContent.value = response.data.data
        exportFormat.value = format
        exportDialogVisible.value = true
      }
    } else {
      ElMessage.error(response.data.error || '导出失败')
    }
  } catch (err) {
    ElMessage.error('导出失败: ' + (err.response?.data?.error || err.message))
  }
}

const downloadExport = () => {
  const blob = new Blob([exportContent.value], {
    type: exportFormat.value === 'json' ? 'application/json' : 'text/markdown'
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test-cases-${new Date().toISOString().slice(0, 10)}.${exportFormat.value === 'json' ? 'json' : 'md'}`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}
</script>

<style scoped>
.test-cases-container {
  max-width: 1400px;
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
  gap: 12px;
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  padding: 60px 0;
}

.case-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.case-id {
  font-weight: bold;
  color: #409eff;
  min-width: 70px;
}

.case-name {
  flex: 1;
  color: #303133;
}

.case-detail {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  color: #303133;
  margin-bottom: 12px;
  font-size: 14px;
}

.detail-section ol {
  padding-left: 20px;
  margin: 0;
}

.detail-section li {
  color: #606266;
  line-height: 1.8;
}

.detail-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #dcdfe6;
}
</style>
