# TARA分析测试数据

本目录包含用于测试TARA一键生成报告功能的示例数据。

## 文件说明

| 文件名 | 类型 | 说明 |
|--------|------|------|
| `assets.json` | JSON | 基础资产清单（10个资产） |
| `complete-assets.json` | JSON | 完整资产清单（12个资产+详细配置） |
| `assets.csv` | CSV | CSV格式资产清单，便于Excel编辑 |
| `architecture.svg` | SVG | 系统架构图，展示车辆E/E架构 |
| `sample-analysis-prompt.txt` | TXT | 示例分析提示词 |

## 快速开始

### 方法1：上传JSON文件（推荐）
```bash
1. 打开TARA系统前端 http://localhost:30021
2. 点击侧边栏 "一键生成报告"
3. 上传 complete-assets.json 文件
4. （可选）上传 architecture.svg 架构图
5. 选择"完整TARA报告"模板
6. 点击"一键生成TARA报告"
```

### 方法2：上传CSV + 图片
```bash
1. 上传 assets.csv 资产清单
2. 上传 architecture.svg 架构图
3. 复制 sample-analysis-prompt.txt 内容到提示词框
4. 选择报告模板并生成
```

## 资产清单

| 资产ID | 资产名称 | 类型 | 域 | 安全等级 |
|--------|----------|------|-----|----------|
| ASSET-001 | 整车控制器 (VCU) | ECU | 动力域 | CAL-4 |
| ASSET-002 | 电池管理系统 (BMS) | ECU | 动力域 | CAL-4 |
| ASSET-003 | 电机控制器 (MCU) | ECU | 动力域 | CAL-3 |
| ASSET-004 | 智能网关 (CGW) | Gateway | 核心 | CAL-4 |
| ASSET-005 | 远程通信单元 (T-Box) | Gateway | 座舱域 | CAL-4 |
| ASSET-006 | 智能驾驶控制器 (ADAS) | ECU | ADAS域 | CAL-4 |
| ASSET-007 | 前视摄像头 | Sensor | ADAS域 | CAL-3 |
| ASSET-008 | 毫米波雷达 | Sensor | ADAS域 | CAL-3 |
| ASSET-009 | 信息娱乐系统 (IVI) | ECU | 座舱域 | CAL-2 |
| ASSET-010 | OBD-II诊断接口 | Interface | 车身域 | CAL-3 |
| ASSET-011 | 电子驻车制动 (EPB) | ECU | 底盘域 | CAL-4 |
| ASSET-012 | 电子稳定程序 (ESP) | ECU | 底盘域 | CAL-4 |

## 网络拓扑

```
                    ┌─────────────────┐
                    │    云端服务      │
                    └────────┬────────┘
                             │ 4G/5G
                    ┌────────┴────────┐
                    │   T-Box (T盒)   │
                    │  WiFi | BT      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴───────┐   ┌───────┴───────┐   ┌───────┴───────┐
│   动力CAN     │   │  智能网关CGW  │   │   底盘CAN     │
│  (500Kbps)    │   │   (Ethernet)  │   │  (500Kbps)    │
├───────────────┤   └───────┬───────┘   ├───────────────┤
│ VCU | BMS     │           │           │ ADAS | ESP    │
│ MCU           │           │           │ EPB | Radar   │
└───────────────┘   ┌───────┴───────┐   └───────────────┘
                    │   车身CAN     │
                    │  (250Kbps)    │
                    ├───────────────┤
                    │ IVI | OBD-II  │
                    └───────────────┘
```

## 预期分析结果

使用此测试数据生成的TARA报告应包含：

### 1. 资产识别
- 12个汽车电子资产及其安全属性
- 网络接口详细配置
- 数据资产分类

### 2. 威胁分析（STRIDE模型）
- 约50-80个威胁场景
- 攻击向量描述
- 攻击可行性评估

### 3. 风险评估
| 风险等级 | 预计数量 | 说明 |
|----------|----------|------|
| CAL-4 (极高) | 5-8个 | 需要立即处理 |
| CAL-3 (高) | 15-20个 | 优先处理 |
| CAL-2 (中) | 20-30个 | 计划处理 |
| CAL-1 (低) | 10-15个 | 可接受 |

### 4. 安全措施建议
- 身份认证措施
- 数据加密方案
- 入侵检测系统
- 安全启动配置

## API测试

### 使用curl测试一键生成API
```bash
curl -X POST http://localhost:30021/api/v1/reports/oneclick \
  -F "files=@complete-assets.json" \
  -F "files=@architecture.svg" \
  -F "template=full" \
  -F "prompt=请进行完整的TARA分析"
```

### 查询生成进度
```bash
curl http://localhost:30021/api/v1/reports/oneclick/{task_id}/progress
```

## 注意事项

1. **文件编码**：CSV文件请使用UTF-8编码
2. **文件大小**：单个文件不超过10MB
3. **图片格式**：支持PNG、JPG、SVG格式
4. **JSON格式**：需符合TARA资产模型规范
