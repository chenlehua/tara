# Project API 调用示例

## 创建项目

### 请求
```bash
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新能源汽车TARA分析",
    "description": "针对BEV车型的威胁分析与风险评估",
    "vehicle_type": "BEV",
    "standard": "ISO/SAE 21434"
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "新能源汽车TARA分析",
    "description": "针对BEV车型的威胁分析与风险评估",
    "vehicle_type": "BEV",
    "standard": "ISO/SAE 21434",
    "status": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "创建成功"
}
```

## 获取项目列表

### 请求
```bash
curl -X GET "http://localhost:8001/api/v1/projects?page=1&page_size=10&keyword=新能源"
```

### 响应
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "新能源汽车TARA分析",
        "status": 1,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

## 获取项目详情

### 请求
```bash
curl -X GET http://localhost:8001/api/v1/projects/1
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "新能源汽车TARA分析",
    "description": "针对BEV车型的威胁分析与风险评估",
    "vehicle_type": "BEV",
    "standard": "ISO/SAE 21434",
    "status": 1,
    "stats": {
      "document_count": 5,
      "asset_count": 23,
      "threat_count": 45,
      "risk_distribution": {
        "critical": 2,
        "high": 8,
        "medium": 15,
        "low": 18,
        "negligible": 2
      }
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T15:45:00Z"
  }
}
```

## 更新项目状态

### 请求
```bash
curl -X PATCH http://localhost:8001/api/v1/projects/1/status?status=2
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": 2,
    "updated_at": "2024-01-17T09:00:00Z"
  },
  "message": "状态更新成功"
}
```

## 克隆项目

### 请求
```bash
curl -X POST http://localhost:8001/api/v1/projects/1/clone \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新能源汽车TARA分析 - 副本"
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "新能源汽车TARA分析 - 副本",
    "status": 0,
    "created_at": "2024-01-17T10:00:00Z"
  },
  "message": "克隆成功"
}
```

## 删除项目

### 请求
```bash
curl -X DELETE http://localhost:8001/api/v1/projects/2
```

### 响应
```json
{
  "success": true,
  "message": "删除成功"
}
```
