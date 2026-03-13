# 数据脱敏模块使用说明

## 概述

数据脱敏模块提供了多种数据隐私保护方法，包括k-匿名、差分隐私和CTABGAN等。该模块已从E:\datamasking项目迁移并集成到当前系统中。

## 功能特性

### 1. 支持的脱敏方法

- **k-匿名**: 通过泛化和抑制技术实现k-匿名，保护个体隐私
- **差分隐私**: 通过添加噪声实现差分隐私，提供严格的隐私保护
- **CTABGAN**: 使用条件表格生成对抗网络生成合成数据

### 2. 应用场景

- **决策支持**: 用于决策支持系统
- **数据展示**: 用于数据可视化展示
- **数据分析**: 用于统计分析
- **预测建模**: 用于机器学习预测

### 3. 安全评分

系统会根据以下因素计算安全评分：
- 记录数量分析
- 字段数量分析
- 场景操作分析
- 记录相关性分析

## API接口

### 1. 上传文件

```http
POST /api/datamasking/upload
Content-Type: multipart/form-data

file: [数据文件]
```

**响应示例:**
```json
{
  "success": true,
  "message": "文件上传成功",
  "result": {
    "file_path": "uploads/datamasking/uuid_filename.csv",
    "file_name": "data.csv",
    "file_size": 1024,
    "headers": ["Age", "Income", "Education", ...]
  }
}
```

### 2. 开始脱敏任务

```http
POST /api/datamasking/start
Content-Type: application/json

{
  "file_path": "uploads/datamasking/uuid_filename.csv",
  "selected_headers": ["Age", "Income", "Education"],
  "record_count": 1000,
  "scenario": "决策",
  "method": "k-匿名",
  "task_name": "脱敏任务_20241201"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "脱敏任务已启动",
  "result": {
    "task_id": 123
  }
}
```

### 3. 获取任务列表

```http
GET /api/datamasking/tasks?page=1&per_page=10
```

**响应示例:**
```json
{
  "success": true,
  "message": "获取任务列表成功",
  "result": {
    "tasks": [
      {
        "id": 123,
        "task_name": "脱敏任务_20241201",
        "status": "completed",
        "progress": 100,
        "method": "k-匿名",
        "scenario": "决策",
        "created_at": "2024-12-01T10:00:00",
        "completed_at": "2024-12-01T10:05:00"
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1,
    "per_page": 10
  }
}
```

### 4. 获取任务详情

```http
GET /api/datamasking/tasks/123
```

**响应示例:**
```json
{
  "success": true,
  "message": "获取任务详情成功",
  "result": {
    "id": 123,
    "task_name": "脱敏任务_20241201",
    "status": "completed",
    "progress": 100,
    "method": "k-匿名",
    "scenario": "决策",
    "result": {
      "safety_score": 0.75,
      "utility_score": 0.85,
      "privacy_score": 0.90,
      "output_file_name": "masked_123_20241201_100500.csv",
      "processing_time": 45.2
    }
  }
}
```

### 5. 下载结果文件

```http
GET /api/datamasking/tasks/123/download
```

### 6. 获取脱敏方法

```http
GET /api/datamasking/methods
```

**响应示例:**
```json
{
  "success": true,
  "message": "获取脱敏方法成功",
  "result": {
    "methods": [
      {
        "id": "k-匿名",
        "name": "k-匿名",
        "description": "通过泛化和抑制技术实现k-匿名，保护个体隐私",
        "parameters": [
          {
            "name": "k",
            "type": "integer",
            "description": "匿名参数k值",
            "default": 3
          }
        ]
      }
    ],
    "scenarios": [
      {
        "id": "决策",
        "name": "决策支持",
        "description": "用于决策支持系统"
      }
    ]
  }
}
```

## 权限要求

- 需要有效的JWT Token
- 需要以下角色之一：ADMIN、RESEARCHER、FAMILY_DOCTOR、ATTENDING_DOCTOR

## 文件格式支持

- CSV文件 (.csv)
- Excel文件 (.xlsx, .xls)
- 文本文件 (.txt)

## 任务状态

- **pending**: 等待处理
- **processing**: 正在处理
- **completed**: 处理完成
- **failed**: 处理失败

## 使用流程

1. **上传文件**: 使用`/upload`接口上传数据文件
2. **配置参数**: 选择脱敏方法、应用场景、处理列等参数
3. **启动任务**: 使用`/start`接口启动脱敏任务
4. **监控进度**: 使用`/tasks`接口查看任务状态和进度
5. **下载结果**: 任务完成后使用`/download`接口下载脱敏结果

## 注意事项

1. 文件大小限制为16MB
2. 脱敏处理是异步进行的，需要轮询任务状态
3. 结果文件会保存在`outputs/datamasking/`目录下
4. 敏感列（如Phone、Id、Hospital）会自动进行特殊处理
5. 系统会根据安全评分自动调整脱敏参数

## 错误处理

所有API都使用统一的错误响应格式：

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

常见错误码：
- `FILE_NOT_FOUND`: 文件不存在
- `INVALID_FILE_FORMAT`: 不支持的文件格式
- `TASK_NOT_FOUND`: 任务不存在
- `PERMISSION_DENIED`: 权限不足
- `PROCESSING_FAILED`: 处理失败

