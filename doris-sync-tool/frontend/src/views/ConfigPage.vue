<template>
  <div class="config-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置管理</span>
          <el-button type="primary" @click="showConfigDialog = true">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>
      
      <el-table :data="configs" stripe>
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewConfig(row.id)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 配置对话框 -->
    <el-dialog v-model="showConfigDialog" title="同步配置" width="800px">
      <el-form :model="configForm" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="configForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        
        <el-divider content-position="left">源数据库 (MySQL)</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主机">
              <el-input v-model="configForm.source.host" placeholder="localhost" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口">
              <el-input-number v-model="configForm.source.port" :min="1" :max="65535" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="configForm.source.user" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input v-model="configForm.source.password" type="password" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="数据库">
          <el-input v-model="configForm.source.database" />
        </el-form-item>
        
        <el-divider content-position="left">目标数据库 (Doris)</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="FE 主机">
              <el-input v-model="configForm.target.fe_host" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="查询端口">
              <el-input-number v-model="configForm.target.query_port" :min="1" :max="65535" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="configForm.target.user" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input v-model="configForm.target.password" type="password" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="数据库">
          <el-input v-model="configForm.target.database" />
        </el-form-item>
        
        <el-divider content-position="left">表配置</el-divider>
        <el-form-item label="表名">
          <el-select v-model="configForm.tables" multiple placeholder="选择要同步的表" style="width: 100%">
            <el-option
              v-for="table in availableTables"
              :key="table"
              :label="table"
              :value="table"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="loadTables">加载表列表</el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { configApi, tableApi } from '@/api'

const configs = ref([])
const showConfigDialog = ref(false)
const availableTables = ref([])

const configForm = ref({
  name: '',
  source: {
    host: 'localhost',
    port: 3306,
    user: '',
    password: '',
    database: ''
  },
  target: {
    fe_host: '',
    query_port: 9030,
    user: '',
    password: '',
    database: ''
  },
  tables: []
})

const loadConfigs = async () => {
  try {
    const res = await configApi.list()
    configs.value = res.configs || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const loadTables = async () => {
  try {
    const res = await tableApi.discover(configForm.value.source)
    availableTables.value = res.tables || []
    ElMessage.success(`发现 ${availableTables.value.length} 张表`)
  } catch (error) {
    ElMessage.error('加载表列表失败：' + error.message)
  }
}

const saveConfig = async () => {
  try {
    const { name, ...configData } = configForm.value
    const tables = configData.tables.map(t => ({ table_name: t, unique_keys: [] }))
    
    await configApi.save(name, {
      ...configData,
      tables
    })
    
    ElMessage.success('配置保存成功')
    showConfigDialog.value = false
    loadConfigs()
  } catch (error) {
    ElMessage.error('保存配置失败')
  }
}

const deleteConfig = async (id) => {
  try {
    await configApi.delete(id)
    ElMessage.success('配置删除成功')
    loadConfigs()
  } catch (error) {
    ElMessage.error('删除配置失败')
  }
}

const viewConfig = (id) => {
  ElMessage.info('查看功能开发中...')
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.config-page {
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
