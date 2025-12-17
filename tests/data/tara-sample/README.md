# TARA Sample Data 测试样例数据

本目录包含用于测试一键生成TARA报告功能的样例数据。

## 文件说明

### project.json
项目基本信息，包含：
- 项目名称、描述、车型信息
- 适用标准（ISO/SAE 21434）
- 项目团队和标签

### assets.json
资产识别数据，包含8个典型车载资产：
- A-001: 车载信息娱乐系统 (IVI)
- A-002: 中央网关 (CGW)
- A-003: 远程信息处理器 (T-Box)
- A-004: 高级驾驶辅助系统 (ADAS)
- A-005: 车身控制器 (BCM)
- A-006: 硬件安全模块 (HSM)
- A-007: OBD诊断接口
- A-008: 动力总成控制器 (PCM)

每个资产包含：
- 接口类型和连接对象
- 网络安全属性（真实性、完整性、机密性等）
- 关键性等级

### threats.json
威胁分析数据，包含10个典型威胁场景：
- 基于STRIDE模型分类
- 包含攻击向量和攻击路径
- WP.29参考映射
- 影响分析（安全、经济、操作、隐私）
- 风险等级（CAL-1至CAL-4）

### measures.json
安全控制措施，包含12项典型措施：
- 预防性控制（SecOC、TLS、安全启动等）
- 检测性控制（IDS、日志审计等）
- 各措施与威胁的关联关系
- ISO 21434参考条款

## 使用方法

### 作为一键生成报告的输入数据
```bash
# 将文件上传到一键生成报告接口
curl -X POST /api/v1/reports/oneclick \
  -F "files=@assets.json" \
  -F "files=@threats.json" \
  -F "template=full" \
  -F "project_name=IVI_TARA_Test"
```

### 作为单元测试数据
```python
import json

with open('tests/data/tara-sample/assets.json') as f:
    assets = json.load(f)['assets']

with open('tests/data/tara-sample/threats.json') as f:
    threats = json.load(f)['threats']
```

## 数据格式说明

### 资产安全属性 (security_attrs)
| 属性 | 说明 |
|------|------|
| authenticity | 真实性 - 确保数据来源可信 |
| integrity | 完整性 - 确保数据未被篡改 |
| non_repudiation | 不可抵赖性 - 确保操作可追溯 |
| confidentiality | 机密性 - 确保数据不被泄露 |
| availability | 可用性 - 确保服务正常运行 |
| authorization | 权限 - 确保访问控制有效 |

### 威胁类型 (STRIDE)
| 类型 | 英文 | 中文 |
|------|------|------|
| S | Spoofing | 欺骗 |
| T | Tampering | 篡改 |
| R | Repudiation | 抵赖 |
| I | Information Disclosure | 信息泄露 |
| D | Denial of Service | 拒绝服务 |
| E | Elevation of Privilege | 权限提升 |

### 风险等级 (CAL)
| 等级 | 描述 | 处置方式 |
|------|------|----------|
| CAL-4 | 严重风险 | 必须立即处置 |
| CAL-3 | 高风险 | 优先处置 |
| CAL-2 | 中等风险 | 计划处置 |
| CAL-1 | 低风险 | 可接受 |

## 参考标准
- ISO/SAE 21434:2021 - Road vehicles — Cybersecurity engineering
- UN Regulation No.155 - Cyber Security
- UN Regulation No.156 - Software Update
- AUTOSAR Cybersecurity Guidelines
