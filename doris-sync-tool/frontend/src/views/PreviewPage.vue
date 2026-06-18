<template>
  <div class="preview-page">
    <el-card>
      <template #header>
        <span>预览生成</span>
      </template>
      
      <el-form :model="previewForm" label-width="120px" inline>
        <el-form-item label="选择配置">
          <el-select v-model="previewForm.configId" placeholder="选择配置" @change="loadConfig">
            <el-option
              v-for="config in configs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择表">
          <el-select v-model="previewForm.tableName" placeholder="选择表" @change="onTableChange">
            <el-option
              v-for="table in availableTables"
              :key="table"
              :label="table"
              :value="table"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="generatePreview" :loading="generating">
            生成预览
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 显示已选择的配置信息 -->
      <el-alert
        v-if="currentConfig && previewForm.tableName"
        title="当前选择"
        type="info"
        show-icon
        style="margin-top: 15px;"
      >
        <template #default>
          <div style="line-height: 1.8;">
            <div><strong>配置名称：</strong>{{ currentConfigName }}</div>
            <div><strong>源数据库：</strong>{{ currentConfig?.source?.host }}:{{ currentConfig?.source?.port }} / {{ currentConfig?.source?.database }}</div>
            <div><strong>目标数据库：</strong>{{ currentConfig?.target?.fe_host }}:{{ currentConfig?.target?.query_port }} / {{ currentConfig?.target?.database }}</div>
            <div><strong>当前表：</strong>{{ previewForm.tableName }}</div>
          </div>
        </template>
      </el-alert>
    </el-card>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>DDL SQL</span>
              <el-button size="small" @click="copySql">复制</el-button>
            </div>
          </template>
          <div class="code-container">
            <pre><code>{{ ddlSql }}</code></pre>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>DataX JSON</span>
              <el-button size="small" @click="copyJson">复制</el-button>
            </div>
          </template>
          <div class="code-container">
            <pre><code>{{ dataxJson }}</code></pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>分桶信息</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="表名">{{ previewResult.table_name }}</el-descriptions-item>
        <el-descriptions-item label="行数">{{ previewResult.row_count?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="分桶数">{{ previewResult.bucket_num }}</el-descriptions-item>
        <el-descriptions-item label="分布列" :span="3">{{ previewResult.distribution_cols?.join(', ') }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { configApi, previewApi } from '@/api'

const configs = ref([])
const availableTables = ref([])
const generating = ref(false)
const ddlSql = ref('-- 请先生成预览')
const dataxJson = ref('-- 请先生成预览')

const previewForm = ref({
  configId: '',
  tableName: ''
})

const previewResult = ref({})

const currentConfig = ref(null)
const currentConfigName = ref('')

const loadConfigs = async () => {
  try {
    const res = await configApi.list()
    configs.value = res.configs || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const loadConfig = async () => {
  if (!previewForm.value.configId) return
  
  try {
    const res = await configApi.get(previewForm.value.configId)
    currentConfig.value = res.config
    currentConfigName.value = res.name
    availableTables.value = res.config.tables?.map(t => t.table_name) || []
    
    if (availableTables.value.length > 0) {
      previewForm.value.tableName = availableTables.value[0]
      onTableChange()
    } else {
      previewForm.value.tableName = ''
    }
  } catch (error) {
    ElMessage.error('加载配置详情失败')
  }
}

const onTableChange = () => {
  // 表选择变化时的处理，可以在这里添加额外逻辑
}

const generatePreview = async () => {
  if (!previewForm.value.configId || !previewForm.value.tableName) {
    ElMessage.warning('请选择配置和表')
    return
  }
  
  generating.value = true
  
  try {
    const res = await previewApi.generate(currentConfig.value, previewForm.value.tableName)
    previewResult.value = res
    ddlSql.value = res.ddl_sql
    dataxJson.value = JSON.stringify(JSON.parse(res.datax_json), null, 2)
    
    ElMessage.success('预览生成成功')
  } catch (error) {
    ElMessage.error('生成预览失败：' + error.message)
    ddlSql.value = '-- 生成失败'
    dataxJson.value = '-- 生成失败'
  } finally {
    generating.value = false
  }
}

const copySql = () => {
  navigator.clipboard.writeText(ddlSql.value)
  ElMessage.success('SQL 已复制到剪贴板')
}

const copyJson = () => {
  navigator.clipboard.writeText(dataxJson.value)
  ElMessage.success('JSON 已复制到剪贴板')
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.preview-page {
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-container {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  max-height: 400px;
  overflow: auto;
}

.code-container pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.code-container code {
  color: #333;
}
</style>
