<template>
  <div class="config-page">
    <!-- 数据库连接管理 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据库连接管理</span>
          <el-button type="primary" @click="showDbConnectionDialog = true">
            <el-icon><Plus /></el-icon>
            新建连接
          </el-button>
        </div>
      </template>
      
      <el-table :data="dbConnections" stripe>
        <el-table-column prop="name" label="连接名称" />
        <el-table-column prop="host" label="主机" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="user" label="用户名" />
        <el-table-column prop="database" label="数据库" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="testConnection(row)">测试连接</el-button>
            <el-button size="small" @click="selectConnection(row)">选择</el-button>
            <el-button size="small" type="danger" @click="deleteConnection(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置管理</span>
          <el-button type="primary" @click="showConfigDialog = true" :disabled="!selectedDbConnection">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>
      
      <el-alert
        v-if="selectedDbConnection"
        title="当前使用的数据库连接"
        type="success"
        show-icon
        style="margin-bottom: 15px;"
      >
        <template #default>
          <div>
            <strong>{{ selectedDbConnection.name }}</strong> - 
            {{ selectedDbConnection.host }}:{{ selectedDbConnection.port }} / 
            {{ selectedDbConnection.database }}
          </div>
        </template>
      </el-alert>
      <el-alert
        v-else
        title="请先选择或创建一个数据库连接"
        type="warning"
        show-icon
        style="margin-bottom: 15px;"
      />
      
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
        <el-alert
          v-if="selectedDbConnection"
          title="使用已保存的数据库连接"
          type="info"
          show-icon
          style="margin-bottom: 15px;"
        >
          <template #default>
            <div>
              {{ selectedDbConnection.host }}:{{ selectedDbConnection.port }} / 
              {{ selectedDbConnection.database }} (用户：{{ selectedDbConnection.user }})
            </div>
          </template>
        </el-alert>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主机">
              <el-input v-model="configForm.source.host" placeholder="localhost" :disabled="!!selectedDbConnection" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口">
              <el-input-number v-model="configForm.source.port" :min="1" :max="65535" :disabled="!!selectedDbConnection" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="configForm.source.user" :disabled="!!selectedDbConnection" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input v-model="configForm.source.password" type="password" show-password :disabled="!!selectedDbConnection" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="数据库">
          <el-select 
            v-model="configForm.source.database" 
            placeholder="选择数据库" 
            style="width: 100%"
            :disabled="!!selectedDbConnection"
            @focus="loadDatabases"
          >
            <el-option
              v-for="db in availableDatabases"
              :key="db"
              :label="db"
              :value="db"
            />
          </el-select>
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
          <el-button @click="loadTables" :disabled="!configForm.source.database">加载表列表</el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 数据库连接对话框 -->
    <el-dialog v-model="showDbConnectionDialog" title="数据库连接" width="600px">
      <el-form :model="dbConnectionForm" label-width="100px">
        <el-form-item label="连接名称">
          <el-input v-model="dbConnectionForm.name" placeholder="例如：生产环境 MySQL" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主机">
              <el-input v-model="dbConnectionForm.connection.host" placeholder="localhost" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口">
              <el-input-number v-model="dbConnectionForm.connection.port" :min="1" :max="65535" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="dbConnectionForm.connection.user" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input v-model="dbConnectionForm.connection.password" type="password" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="数据库">
          <el-input v-model="dbConnectionForm.connection.database" placeholder="默认数据库（可选）" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showDbConnectionDialog = false">取消</el-button>
        <el-button @click="testDbConnection">测试连接</el-button>
        <el-button type="primary" @click="saveDbConnection">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { configApi, tableApi, dbConnectionApi } from '@/api'

const configs = ref([])
const dbConnections = ref([])
const selectedDbConnection = ref(null)
const showConfigDialog = ref(false)
const showDbConnectionDialog = ref(false)
const availableTables = ref([])
const availableDatabases = ref([])

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

const dbConnectionForm = ref({
  name: '',
  connection: {
    host: 'localhost',
    port: 3306,
    user: '',
    password: '',
    database: ''
  }
})

// 监听选中连接变化，自动填充配置表单
watch(selectedDbConnection, (newVal) => {
  if (newVal) {
    configForm.value.source.host = newVal.host
    configForm.value.source.port = newVal.port
    configForm.value.source.user = newVal.user
    // 密码不自动填充，需要用户手动输入或从后端获取
    configForm.value.source.database = newVal.database || ''
  }
}, { deep: true })

const loadConfigs = async () => {
  try {
    const res = await configApi.list()
    configs.value = res.configs || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const loadDbConnections = async () => {
  try {
    const res = await dbConnectionApi.list()
    dbConnections.value = res.connections || []
  } catch (error) {
    ElMessage.error('加载数据库连接列表失败')
  }
}

const testConnection = async (row) => {
  try {
    const res = await dbConnectionApi.test(row)
    if (res.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    ElMessage.error('测试连接失败：' + error.message)
  }
}

const selectConnection = (row) => {
  selectedDbConnection.value = row
  ElMessage.success(`已选择连接：${row.name}`)
}

const deleteConnection = async (id) => {
  try {
    await dbConnectionApi.delete(id)
    ElMessage.success('连接删除成功')
    loadDbConnections()
    if (selectedDbConnection.value?.id === id) {
      selectedDbConnection.value = null
    }
  } catch (error) {
    ElMessage.error('删除连接失败')
  }
}

const saveDbConnection = async () => {
  try {
    await dbConnectionApi.save(dbConnectionForm.value.name, dbConnectionForm.value.connection)
    ElMessage.success('数据库连接保存成功')
    showDbConnectionDialog.value = false
    loadDbConnections()
    // 重置表单
    dbConnectionForm.value = {
      name: '',
      connection: {
        host: 'localhost',
        port: 3306,
        user: '',
        password: '',
        database: ''
      }
    }
  } catch (error) {
    ElMessage.error('保存数据库连接失败')
  }
}

const testDbConnection = async () => {
  try {
    const res = await dbConnectionApi.test(dbConnectionForm.value.connection)
    if (res.success) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    ElMessage.error('测试连接失败：' + error.message)
  }
}

const loadDatabases = async () => {
  if (!configForm.value.source.host || !configForm.value.source.user) {
    ElMessage.warning('请先填写主机和用户名信息')
    return
  }
  
  try {
    const res = await dbConnectionApi.listDatabases(configForm.value.source)
    if (res.success) {
      availableDatabases.value = res.databases || []
      ElMessage.success(`发现 ${availableDatabases.value.length} 个数据库`)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    ElMessage.error('加载数据库列表失败：' + error.message)
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
  loadDbConnections()
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
