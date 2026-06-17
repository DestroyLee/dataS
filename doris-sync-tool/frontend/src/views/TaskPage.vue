<template>
  <div class="task-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务执行</span>
          <el-button type="primary" @click="showExecuteDialog = true">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" stripe>
        <el-table-column prop="id" label="任务 ID" width="100" />
        <el-table-column prop="config_name" label="配置名称" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : undefined" />
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewLogs(row.id)">日志</el-button>
            <el-button 
              v-if="row.status === 'running'" 
              size="small" 
              type="warning" 
              @click="cancelTask(row.id)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 执行任务对话框 -->
    <el-dialog v-model="showExecuteDialog" title="执行同步任务" width="600px">
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="选择配置">
          <el-select v-model="executeForm.configId" placeholder="选择配置" style="width: 100%">
            <el-option
              v-for="config in configs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择表">
          <el-select v-model="executeForm.tableNames" multiple placeholder="选择要同步的表" style="width: 100%">
            <el-option
              v-for="table in availableTables"
              :key="table"
              :label="table"
              :value="table"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showExecuteDialog = false">取消</el-button>
        <el-button type="primary" @click="executeTask" :loading="executing">执行</el-button>
      </template>
    </el-dialog>
    
    <!-- 日志对话框 -->
    <el-dialog v-model="showLogDialog" title="任务日志" width="800px">
      <div class="log-container">
        <div v-for="(log, index) in currentLogs" :key="index" class="log-line">
          {{ log }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { configApi, taskApi } from '@/api'

const tasks = ref([])
const configs = ref([])
const availableTables = ref([])
const showExecuteDialog = ref(false)
const showLogDialog = ref(false)
const executing = ref(false)
const currentLogs = ref([])

const executeForm = ref({
  configId: '',
  tableNames: []
})

const loadTasks = async () => {
  try {
    const res = await taskApi.list()
    tasks.value = res.tasks || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const loadConfigs = async () => {
  try {
    const res = await configApi.list()
    configs.value = res.configs || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const loadTables = async () => {
  if (!executeForm.value.configId) return
  
  try {
    const res = await configApi.get(executeForm.value.configId)
    availableTables.value = res.config.tables?.map(t => t.table_name) || []
    executeForm.value.tableNames = [...availableTables.value]
  } catch (error) {
    ElMessage.error('加载表列表失败')
  }
}

const executeTask = async () => {
  if (!executeForm.value.configId) {
    ElMessage.warning('请选择配置')
    return
  }
  
  executing.value = true
  
  try {
    await taskApi.execute({
      config_id: executeForm.value.configId,
      table_names: executeForm.value.tableNames
    })
    
    ElMessage.success('任务已提交')
    showExecuteDialog.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('提交任务失败：' + error.message)
  } finally {
    executing.value = false
  }
}

const cancelTask = async (taskId) => {
  try {
    await taskApi.cancel(taskId)
    ElMessage.success('任务已取消')
    loadTasks()
  } catch (error) {
    ElMessage.error('取消任务失败')
  }
}

const viewLogs = async (taskId) => {
  try {
    const res = await taskApi.getLogs(taskId)
    currentLogs.value = res.logs || []
    showLogDialog.value = true
  } catch (error) {
    ElMessage.error('加载日志失败')
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '等待中',
    running: '运行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status
}

onMounted(() => {
  loadTasks()
  loadConfigs()
  // 每 5 秒刷新一次任务状态
  setInterval(loadTasks, 5000)
})
</script>

<style scoped>
.task-page {
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  max-height: 400px;
  overflow: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.log-line {
  line-height: 1.6;
  border-bottom: 1px solid #eee;
}

.log-line:last-child {
  border-bottom: none;
}
</style>
