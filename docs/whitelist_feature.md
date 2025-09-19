# 白名单功能说明文档

## 功能概述

本系统新增了IP白名单和工作时间白名单功能，用于控制用户访问医疗数据的权限。每次获取医疗数据时，系统会自动检查用户的IP地址和访问时间，并更新相应的统计信息。

## 功能特性

### 1. IP白名单管理
- 支持单个IP地址精确匹配
- 支持CIDR格式的IP地址段（如：192.168.0.0/16）
- 支持启用/禁用白名单记录
- 提供IP白名单的增删改查功能

### 2. 工作时间白名单管理
- 支持按星期几设置工作时间段
- 支持多个时间段设置
- 自动检测时间段重叠
- 提供工作时间白名单的增删改查功能

### 3. 自动统计更新
- 每次访问医疗数据时自动检查IP和时间
- 更新`AccessLocationTracker`的IP访问统计
- 更新`AccessTimeTracker`的时间访问统计
- 在API响应中返回检查结果

## 数据库模型

### IPWhitelist（IP白名单）
```sql
CREATE TABLE sys_ip_whitelist (
    id INTEGER PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### WorkingTimeWhitelist（工作时间白名单）
```sql
CREATE TABLE sys_working_time_whitelist (
    id INTEGER PRIMARY KEY,
    day_of_week INTEGER NOT NULL,  -- 0-6, 0为周日
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## API接口

### IP白名单管理

#### 获取IP白名单列表
```
GET /api/whitelist/ip-whitelist
```

#### 添加IP白名单
```
POST /api/whitelist/ip-whitelist
Content-Type: application/json

{
    "ip_address": "192.168.1.100",
    "description": "办公室IP",
    "is_active": true
}
```

#### 更新IP白名单
```
PUT /api/whitelist/ip-whitelist/{id}
Content-Type: application/json

{
    "ip_address": "192.168.1.100",
    "description": "更新后的描述",
    "is_active": true
}
```

#### 删除IP白名单
```
DELETE /api/whitelist/ip-whitelist/{id}
```

### 工作时间白名单管理

#### 获取工作时间白名单列表
```
GET /api/whitelist/working-time-whitelist
```

#### 添加工作时间白名单
```
POST /api/whitelist/working-time-whitelist
Content-Type: application/json

{
    "day_of_week": 1,  // 1=周一
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "description": "周一工作时间",
    "is_active": true
}
```

#### 更新工作时间白名单
```
PUT /api/whitelist/working-time-whitelist/{id}
Content-Type: application/json

{
    "day_of_week": 1,
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "description": "更新后的描述",
    "is_active": true
}
```

#### 删除工作时间白名单
```
DELETE /api/whitelist/working-time-whitelist/{id}
```

### 白名单状态检查

#### 检查当前状态
```
GET /api/whitelist/check-status
```

返回结果：
```json
{
    "code": 200,
    "msg": "检查成功",
    "data": {
        "client_ip": "192.168.1.100",
        "is_whitelist_ip": true,
        "is_working_time": true,
        "access_allowed": true
    }
}
```

## 受影响的API接口

以下医疗数据获取接口已集成白名单检查功能：

1. `POST /api/medical_record/get_record_data` - 获取医疗记录数据
2. `GET /api/medical_record/get_mypatients` - 获取我的患者
3. `GET /api/medical_record/get_patient/{user_id}` - 根据身份证号查询患者
4. `POST /api/medical_record/get_sensitive_data` - 获取敏感数据

这些接口的响应中会包含以下额外字段：
```json
{
    "client_ip": "192.168.1.100",
    "is_whitelist_ip": true,
    "is_working_time": true,
    // ... 其他原有字段
}
```

## 初始化数据

系统提供了默认的白名单初始化数据：

### IP白名单默认数据
- `127.0.0.1` - 本地回环地址
- `192.168.0.0/16` - 内网地址段
- `10.0.0.0/8` - 内网地址段
- `172.16.0.0/12` - 内网地址段

### 工作时间默认数据
- 周一至周五：09:00-17:00
- 周六：09:00-12:00
- 周日：无工作时间

## 安全特性

1. **容错机制**：如果白名单检查失败，默认允许访问，避免影响正常业务
2. **IP获取优先级**：优先从代理头获取真实IP，支持负载均衡环境
3. **时间重叠检测**：防止设置冲突的工作时间段
4. **数据完整性**：所有操作都有事务保护，确保数据一致性

## 使用建议

1. **生产环境**：建议配置具体的IP地址段，避免使用过于宽泛的网段
2. **工作时间**：根据实际业务需求设置合理的工作时间段
3. **监控**：定期检查访问统计，识别异常访问模式
4. **备份**：定期备份白名单配置，便于恢复和迁移

## 注意事项

1. 白名单检查不会阻止访问，只会记录统计信息
2. 如果未配置白名单，系统默认允许所有IP和时间访问
3. 时间检查基于服务器本地时间，请确保服务器时间准确
4. IP检查支持IPv4和IPv6地址格式
