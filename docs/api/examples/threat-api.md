# Threat API 调用示例

## 创建威胁

### 请求
```bash
curl -X POST http://localhost:8004/api/v1/threats \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "asset_id": 5,
    "threat_name": "CAN总线消息注入",
    "threat_type": "Tampering",
    "description": "攻击者通过OBD接口向CAN总线注入恶意消息",
    "attack_vector": "physical",
    "impact_safety": "major",
    "impact_financial": "moderate",
    "impact_operational": "major",
    "impact_privacy": "negligible"
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 12,
    "project_id": 1,
    "asset_id": 5,
    "threat_name": "CAN总线消息注入",
    "threat_type": "Tampering",
    "description": "攻击者通过OBD接口向CAN总线注入恶意消息",
    "attack_vector": "physical",
    "impact_safety": "major",
    "impact_financial": "moderate",
    "impact_operational": "major",
    "impact_privacy": "negligible",
    "created_at": "2024-01-15T14:30:00Z"
  }
}
```

## STRIDE 自动分析

### 请求
```bash
curl -X POST http://localhost:8004/api/v1/threats/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "asset_id": 5
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "threats": [
      {
        "threat_name": "CAN消息伪造",
        "threat_type": "Spoofing",
        "description": "伪造来自其他ECU的CAN消息"
      },
      {
        "threat_name": "CAN消息篡改",
        "threat_type": "Tampering",
        "description": "篡改在途CAN消息内容"
      },
      {
        "threat_name": "CAN总线洪泛",
        "threat_type": "Denial of Service",
        "description": "发送大量消息占用总线带宽"
      }
    ],
    "analysis_time": 2.5
  }
}
```

## 创建攻击路径

### 请求
```bash
curl -X POST http://localhost:8004/api/v1/attack-paths \
  -H "Content-Type: application/json" \
  -d '{
    "threat_risk_id": 12,
    "name": "OBD接口物理攻击",
    "description": "通过OBD诊断口实施的物理攻击",
    "steps": [
      {
        "order": 1,
        "action": "物理接入",
        "description": "获取车辆物理访问权限",
        "target": "车辆"
      },
      {
        "order": 2,
        "action": "连接OBD接口",
        "description": "将攻击设备连接到OBD-II端口",
        "target": "OBD端口"
      },
      {
        "order": 3,
        "action": "CAN消息注入",
        "description": "通过OBD向CAN总线发送恶意消息",
        "target": "CAN总线"
      }
    ],
    "expertise": 3,
    "elapsed_time": 1,
    "equipment": 2,
    "knowledge": 2,
    "window_of_opportunity": 1
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "id": 5,
    "threat_risk_id": 12,
    "name": "OBD接口物理攻击",
    "steps": [...],
    "attack_potential": 9,
    "feasibility_rating": "high",
    "created_at": "2024-01-15T15:00:00Z"
  }
}
```

## 风险评估

### 请求
```bash
curl -X POST http://localhost:8004/api/v1/risks/assess \
  -H "Content-Type: application/json" \
  -d '{
    "threat_id": 12,
    "impact_level": "major",
    "likelihood": "high"
  }'
```

### 响应
```json
{
  "success": true,
  "data": {
    "threat_id": 12,
    "risk_level": "critical",
    "risk_value": 20,
    "impact_level": "major",
    "likelihood": "high",
    "cal_level": "CAL3",
    "treatment": "reduce"
  }
}
```

## 获取风险矩阵

### 请求
```bash
curl -X GET "http://localhost:8004/api/v1/risks/matrix?project_id=1"
```

### 响应
```json
{
  "success": true,
  "data": {
    "matrix": {
      "rows": ["severe", "major", "moderate", "minor", "negligible"],
      "columns": ["very_low", "low", "medium", "high", "very_high"],
      "cells": [
        ["high", "critical", "critical", "critical", "critical"],
        ["medium", "high", "critical", "critical", "critical"],
        ["low", "medium", "high", "critical", "critical"],
        ["negligible", "low", "medium", "high", "high"],
        ["negligible", "negligible", "low", "medium", "medium"]
      ]
    },
    "threats": [
      {
        "id": 12,
        "name": "CAN总线消息注入",
        "impact": "major",
        "likelihood": "high",
        "risk_level": "critical",
        "position": [1, 3]
      }
    ],
    "summary": {
      "critical": 2,
      "high": 5,
      "medium": 8,
      "low": 10,
      "negligible": 3
    }
  }
}
```

## 推荐控制措施

### 请求
```bash
curl -X GET "http://localhost:8004/api/v1/threats/12/controls"
```

### 响应
```json
{
  "success": true,
  "data": {
    "controls": [
      {
        "name": "CAN消息认证",
        "description": "使用MAC对CAN消息进行认证",
        "type": "preventive",
        "category": "technical",
        "effectiveness": "high",
        "priority": 1
      },
      {
        "name": "入侵检测系统",
        "description": "部署CAN总线入侵检测系统",
        "type": "detective",
        "category": "technical",
        "effectiveness": "medium",
        "priority": 2
      },
      {
        "name": "OBD接口访问控制",
        "description": "实施OBD端口的物理和逻辑访问控制",
        "type": "preventive",
        "category": "physical",
        "effectiveness": "medium",
        "priority": 3
      }
    ]
  }
}
```
