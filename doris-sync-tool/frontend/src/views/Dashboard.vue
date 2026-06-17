<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用 Doris Sync Tool</span>
        </div>
      </template>
      
      <div class="stats-grid">
        <el-statistic title="配置数量" :value="configCount" />
        <el-statistic title="任务总数" :value="taskCount" />
        <el-statistic title="成功任务" :value="successCount" />
        <el-statistic title="运行中任务" :value="runningCount" />
      </div>
      
      <div class="quick-actions">
        <h3>快速操作</h3>
        <el-space>
          <el-button type="primary" @click="$router.push('/config')">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
          <el-button type="success" @click="$router.push('/preview')">
            <el-icon><Document /></el-icon>
            预览生成
          </el-button>
          <el-button type="warning" @click="$router.push('/tasks')">
            <el-icon><Operation /></el-icon>
            执行任务
          </el-button>
        </el-space>
      </div>
    </el-card>
    
    <el-card class="info-card" style="margin-top: 20px;">
      <template #header>
        <span>使用说明</span>
      </template>
      <ol>
        <li>在<strong>配置管理</strong>页面创建 MySQL 到 Doris 的同步配置</li>
        <li>在<strong>预览生成</strong>页面查看生成的 DDL SQL 和 DataX 配置</li>
        <li>在<strong>任务执行</strong>页面执行同步任务并查看进度</li>
      </ol>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { configApi, taskApi } from '@/api'

const configCount = ref(0)
const taskCount = ref(0)
const successCount = ref(0)
const runningCount = ref(0)

onMounted(async () => {
  try {
    const configRes = await configApi.list()
    configCount.value = configRes.total || 0
    
    const taskRes = await taskApi.list()
    taskCount.value = taskRes.total || 0
    successCount.value = taskRes.tasks?.filter(t => t.status === 'success').length || 0
    runningCount.value = taskRes.tasks?.filter(t => t.status === 'running').length || 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: 30px 0;
}

.quick-actions h3 {
  margin-bottom: 15px;
}

.info-card ol li {
  margin: 10px 0;
  line-height: 1.8;
}
</style>
