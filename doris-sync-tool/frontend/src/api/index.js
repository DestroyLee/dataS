import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 配置管理 API
export const configApi = {
  list: () => request.get('/config/list'),
  get: (id) => request.get(`/config/${id}`),
  save: (name, config) => request.post('/config/save', { name, config }),
  update: (id, name, config) => request.put(`/config/${id}`, { name, config }),
  delete: (id) => request.delete(`/config/${id}`)
}

// 数据库连接管理 API
export const dbConnectionApi = {
  list: () => request.get('/db-connection/list'),
  get: (id) => request.get(`/db-connection/${id}`),
  save: (name, connection) => request.post('/db-connection/save', { name, connection }),
  update: (id, name, connection) => request.put(`/db-connection/${id}`, { name, connection }),
  delete: (id) => request.delete(`/db-connection/${id}`),
  test: (connection) => request.post('/db-connection/test', connection),
  listDatabases: (connection) => request.post('/db-connection/databases/list', connection)
}

// 表发现 API
export const tableApi = {
  discover: (params) => request.post('/preview/tables/discover', params),
  getMeta: (tableName, params) => request.post(`/preview/tables/${tableName}/meta`, params)
}

// 预览 API
export const previewApi = {
  generate: (config, tableName) => request.post('/preview/ddl', { config, table_name: tableName })
}

// 任务 API
export const taskApi = {
  execute: (data) => request.post('/tasks/execute', data),
  list: () => request.get('/tasks/list'),
  get: (id) => request.get(`/tasks/${id}`),
  getLogs: (id) => request.get(`/tasks/${id}/logs`),
  cancel: (id) => request.post(`/tasks/${id}/cancel`)
}
