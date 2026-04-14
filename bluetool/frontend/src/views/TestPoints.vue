<template>
  <div class="test-points-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><List /></el-icon>
            测试点管理
            <el-tag v-if="testPoints.length > 0" type="primary">
              共 {{ testPoints.length }} 个
            </el-tag>
          </h2>
          <div class="header-actions">
            <el-button @click="addTestPoint">
              <el-icon><Plus /></el-icon> 新增测试点
            </el-button>
            <el-button type="primary" @click="generateTestCases" :loading="generating">
              <el-icon><DocumentChecked /></el-icon> 生成测试用例
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="testPoints.length === 0" class="empty-state">
        <el-empty description="暂无测试点">
          <el-button type="primary" @click="$router.push('/upload')">
            去上传文档
          </el-button>
        </el-empty>
      </div>

      <div v-else>
        <el-table
          :data="testPoints"
          style="width: 100%"
          border
          stripe
          v-loading="loading"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="test_point_id" label="测试点编号" width="120" />
          <el-table-column prop="category" label="分类" width="100">
            <template #default="scope">
              <el-tag :type="getCategoryType(scope.row.category)" size="small">
                {{ scope.row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
          <el-table-column prop="test_type" label="测试类型" width="120">
            <template #default="scope">
              <el-tag :type="getTestType(scope.row.test_type)" size="small">
                {{ scope.row.test_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="scope">
              <el-tag
                :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'"
                size="small"
              >
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="editTestPoint(scope.row, scope.$index)">
                编辑
              </el-button>
              <el-button link type="danger" @click="deleteTestPoint(scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="table-actions">
          <el-button @click="saveToLocal">
            <el-icon><Download /></el-icon> 保存到本地
          </el-button>
          <el-button type="primary" @click="generateTestCases" :loading="generating">
            <el-icon><DocumentChecked /></el-icon> 生成测试用例
          </el-button>
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑测试点' : '新增测试点'"
      width="600px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
            <el-option label="功能点" value="功能点" />
            <el-option label="交互点" value="交互点" />
            <el-option label="异常点" value="异常点" />
            <el-option label="边界点" value="边界点" />
            <el-option label="校验点" value="校验点" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入测试点描述"
          />
        </el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="form.test_type" placeholder="选择测试类型" style="width: 100%">
            <el-option label="功能测试" value="功能测试" />
            <el-option label="交互测试" value="交互测试" />
            <el-option label="异常测试" value="异常测试" />
            <el-option label="边界测试" value="边界测试" />
            <el-option label="权限测试" value="权限测试" />
            <el-option label="性能测试" value="性能测试" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio-button label="高" />
            <el-radio-button label="中" />
            <el-radio-button label="低" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTestPoint">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const testPoints = ref([])
const loading = ref(false)
const generating = ref(false)
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingIndex = ref(-1)

const form = ref({
  test_point_id: '',
  category: '功能点',
  description: '',
  test_type: '功能测试',
  priority: '中',
  chunk_id: 0
})

onMounted(() => {
  const saved = localStorage.getItem('currentTestPoints')
  if (saved) {
    try {
      testPoints.value = JSON.parse(saved)
    } catch (e) {
      console.error('解析测试点失败:', e)
    }
  }
})

const getCategoryType = (category) => {
  const map = {
    '功能点': 'primary',
    '交互点': 'success',
    '异常点': 'danger',
    '边界点': 'warning',
    '校验点': 'info'
  }
  return map[category] || 'info'
}

const getTestType = (type) => {
  const map = {
    '功能测试': 'primary',
    '交互测试': 'success',
    '异常测试': 'danger',
    '边界测试': 'warning',
    '权限测试': 'info',
    '性能测试': ''
  }
  return map[type] || ''
}

const addTestPoint = () => {
  isEditing.value = false
  editingIndex.value = -1
  form.value = {
    test_point_id: `TP-${String(testPoints.value.length + 1).padStart(3, '0')}`,
    category: '功能点',
    description: '',
    test_type: '功能测试',
    priority: '中',
    chunk_id: 0
  }
  dialogVisible.value = true
}

const editTestPoint = (point, index) => {
  isEditing.value = true
  editingIndex.value = index
  form.value = { ...point }
  dialogVisible.value = true
}

const saveTestPoint = () => {
  if (!form.value.description.trim()) {
    ElMessage.warning('请输入测试点描述')
    return
  }

  if (isEditing.value) {
    testPoints.value[editingIndex.value] = { ...form.value }
  } else {
    testPoints.value.push({ ...form.value })
  }

  localStorage.setItem('currentTestPoints', JSON.stringify(testPoints.value))
  dialogVisible.value = false
  ElMessage.success(isEditing.value ? '编辑成功' : '新增成功')
}

const deleteTestPoint = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试点吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    testPoints.value.splice(index, 1)

    testPoints.value.forEach((point, idx) => {
      point.test_point_id = `TP-${String(idx + 1).padStart(3, '0')}`
    })

    localStorage.setItem('currentTestPoints', JSON.stringify(testPoints.value))
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const saveToLocal = () => {
  const data = JSON.stringify(testPoints.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test-points-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已保存到本地')
}

const generateTestCases = async () => {
  if (testPoints.value.length === 0) {
    ElMessage.warning('请先添加测试点')
    return
  }

  generating.value = true

  try {
    const response = await axios.post('/api/generate-test-cases', {
      test_points: testPoints.value,
      model: 'gpt-3.5-turbo'
    })

    if (response.data.test_cases) {
      localStorage.setItem('currentTestCases', JSON.stringify(response.data.test_cases))
      ElMessage.success(`成功生成 ${response.data.test_cases.length} 条测试用例`)
      router.push('/test-cases')
    } else {
      ElMessage.error(response.data.error || '生成测试用例失败')
    }
  } catch (err) {
    ElMessage.error('生成测试用例失败: ' + (err.response?.data?.error || err.message))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.test-points-container {
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

.table-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
