# 单元测试

## 已完成的测试

### 1. 模块导入测试 ✅
- 所有核心模块可正常导入
- 依赖库安装正确

### 2. 配置加载测试 ✅
- YAML 配置文件解析正常
- 配置验证逻辑工作正常

### 3. 模板渲染测试 ✅
- DDL Jinja2 模板渲染正确
- DataX JSON 模板渲染正确
- JSON 格式验证通过

### 4. 分桶策略测试 ✅
- 自动分桶算法工作正常：
  - 0 行 → 1 个分桶
  - 50 万行 → 1 个分桶
  - 100 万行 → 1 个分桶
  - 500 万行 → 8 个分桶
  - 2000 万行 → 32 个分桶
  - 1 亿行 → 64 个分桶（上限）

### 5. 完整流程模拟测试 ✅
- 从元数据到 DDL 生成全流程正常
- Unique Key 模型表生成正确
- 普通表（无 Unique Key）生成正确
- DataX JSON 配置条件渲染正确（有/无 load_props）

## 待人工验证项

### 1. 真实 MySQL 连接测试
需要真实 MySQL 环境验证：
```bash
python main.py --config config/sync_task.yaml --output ./output
```

### 2. Doris DDL 执行测试
在 Doris 中执行生成的 SQL 文件，验证：
- 表结构是否正确
- Unique Key 约束是否生效
- 分桶数是否合理

### 3. DataX 任务执行测试
使用 DataX 运行生成的 JSON 配置：
```bash
python $DATAX_HOME/bin/datax.py output/datax/t_order_info.json
```

## 下一步建议

1. **准备测试环境**：配置真实的 MySQL 和 Doris 连接信息
2. **运行端到端测试**：执行完整流程生成实际文件
3. **验证输出**：检查生成的 SQL 和 JSON 是否符合预期
4. **集成到工作流**：将工具应用到实际业务场景
