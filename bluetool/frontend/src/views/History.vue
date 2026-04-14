<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Clock /></el-icon>
            历史记录
          </h2>
          <el-button type="danger" @click="clearHistory" v-if="history.length > 0">
            <el-icon><Delete /></el-icon> 清空历史
          </el-button>
        </div>
      </template>

      <div v-if="history.length === 0" class="empty-state">
        <el-empty description="暂无历史记录">
          <el-button type="primary" @click="$router.push('/upload')">
            去上传文档
          </el-button>
        </el-empty>
      </div>

      <el-table v-else :data="history" style="width: 100%" border stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="scope">
            <el-icon><Document /></el-icon>
            {{ scope.row.original_name }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'completed' ? '已完成' : '已上传' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="continueParse(scope.row)">
              继续解析
            </el-button>
            <el-button link type="danger" @click="deleteItem(scope.$index)">
              删除
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
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const history = ref([])

onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  try {
    const response = await axios.get('/api/history')
    if (response.data.success) {
      history.value = response.data.history.reverse()
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

const continueParse = (file) => {
  router.push(`/parse/${file.id}`)
}

const deleteItem = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    history.value.splice(index, 1)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    history.value = []
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.history-container {
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

.empty-state {
  padding: 60px 0;
}
</style>
