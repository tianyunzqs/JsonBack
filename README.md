# FastAPI JSON工具箱服务启动说明

## 功能特性

### 1. JSON合并功能
- 支持多个JSON数据集的递归合并
- 使用优化的`recurrence_combine`算法
- 自动处理字段差异，缺失字段填充为null

### 2. 文件上传和解析
- **支持格式**：CSV、Excel (.xlsx, .xls)、JSON、JSONL
- **文件大小限制**：最大10MB
- **自动编码检测**：支持UTF-8等编码格式

### 3. 混合合并模式
- 支持文件+JSON文本的混合输入
- 灵活的数据源组合

## 安装依赖

```bash
pip install -r requirements.txt
```

### 主要依赖包
- `fastapi`: Web框架
- `uvicorn`: ASGI服务器
- `pandas`: 数据处理（Excel、CSV支持）
- `openpyxl`: Excel文件读取
- `python-multipart`: 文件上传支持

## 启动服务

### 方法1：直接运行
```bash
python fastapi_server.py
```

### 方法2：使用uvicorn
```bash
uvicorn fastapi_server:app --host 0.0.0.0 --port 3001 --reload
```

## API接口

### 1. 健康检查
- **URL**: `GET http://localhost:3001/api/health`
- **功能**: 检查服务状态

### 2. JSON合并
- **URL**: `POST http://localhost:3001/api/merge`
- **功能**: 合并多个JSON数据集
- **请求格式**:
```json
{
  "datasets": [
    [{"name": "张三", "age": 25}],
    [{"name": "李四", "age": 30}]
  ]
}
```

### 3. 文件上传解析
- **URL**: `POST http://localhost:3001/api/upload`
- **功能**: 上传并解析文件
- **请求**: 使用`multipart/form-data`格式

### 4. 文件与JSON合并
- **URL**: `POST http://localhost:3001/api/merge-with-file`
- **功能**: 文件与JSON文本数据合并
- **请求**: 文件 + 可选的JSON文本

## 前端集成

前端页面已更新，支持：
- 单个数据集输入
- 文件上传（拖拽或点击选择）
- 实时预览和验证
- 美观的结果展示

## 使用示例

### 1. 启动服务
```bash
cd /path/to/your/project
python fastapi_server.py
```

### 2. 访问API文档
打开浏览器访问：`http://localhost:3001/docs`

### 3. 测试接口
可以使用Postman或curl测试各个接口

## 注意事项

1. **文件格式要求**：
   - CSV：必须有标题行，逗号分隔
   - Excel：支持.xlsx和.xls格式
   - JSON：必须是对象数组格式
   - JSONL：每行一个JSON对象

2. **性能考虑**：
   - 大文件处理可能需要较长时间
   - 建议文件大小控制在10MB以内

3. **错误处理**：
   - 详细的错误信息返回
   - 支持多种异常情况

## 故障排除

### 常见问题

1. **端口占用**：
   ```bash
   # 查看端口占用
   netstat -ano | findstr :3001
   # 或使用其他端口
   uvicorn fastapi_server:app --port 3002
   ```

2. **依赖安装失败**：
   ```bash
   # 升级pip
   python -m pip install --upgrade pip
   # 使用国内镜像
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
   ```

3. **文件上传失败**：
   - 检查文件格式是否正确
   - 确认文件大小是否超限
   - 查看服务日志获取详细错误信息

## 开发模式

启动时添加`--reload`参数可实现热重载：
```bash
uvicorn fastapi_server:app --reload --port 3001
```

这样修改代码后服务会自动重启，方便开发调试。
