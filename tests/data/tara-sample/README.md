# TARA 分析示例数据

本目录包含用于生成完整TARA分析报告的示例数据文件。这些数据基于ISO/SAE 21434标准，以车载信息娱乐系统(IVI)为分析对象。

## 文件说明

| 文件名 | 格式 | 说明 |
|--------|------|------|
| `project_info.json` | JSON | 项目基本信息和分析范围定义 |
| `assets.json` | JSON | 资产清单（详细版，含安全属性） |
| `assets.csv` | CSV | 资产清单（简化版，可用Excel编辑） |
| `threats.json` | JSON | 威胁场景列表（STRIDE分类） |
| `control_measures.json` | JSON | 安全控制措施 |
| `system_description.md` | Markdown | 系统架构描述文档 |

## 数据统计

- **资产数量**: 15个
  - ECU: 2个 (SOC, MCU)
  - 存储: 2个 (DDR, UFS)
  - 通信模块: 3个 (WiFi, BT, 4G/5G)
  - 接口: 4个 (CAN网关, 以太网, USB, 诊断)
  - 数据: 3个 (用户数据, 车辆状态, 密钥)
  - 服务: 1个 (OTA)

- **威胁数量**: 12个
  - Spoofing (欺骗): 2个
  - Tampering (篡改): 3个
  - Repudiation (抵赖): 1个
  - Information Disclosure (信息泄露): 2个
  - Denial of Service (拒绝服务): 2个
  - Elevation of Privilege (权限提升): 2个

- **控制措施数量**: 22个

- **风险分布**:
  - CAL-4 (极高): 6个
  - CAL-3 (高): 3个
  - CAL-2 (中): 3个
  - CAL-1 (低): 0个

## 使用方法

### 方法1: 一键上传生成报告
1. 在TARA Pro系统中选择"一键生成报告"
2. 上传以下文件：
   - `assets.json` 或 `assets.csv`
   - `project_info.json`（可选）
   - `system_description.md`（可选）
3. 选择报告模板（推荐：ISO 21434）
4. 点击生成，等待分析完成
5. 下载Excel/PDF/Word格式报告

### 方法2: API调用
```bash
# 创建项目
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Content-Type: application/json" \
  -d @project_info.json

# 上传资产
curl -X POST http://localhost:8003/api/v1/assets/batch \
  -H "Content-Type: application/json" \
  -d @assets.json

# 触发威胁分析
curl -X POST http://localhost:8004/api/v1/threats/analyze-project \
  -d "project_id=1"

# 生成报告
curl -X POST http://localhost:8005/api/v1/reports/generate \
  -d "project_id=1&format=xlsx"
```

### 方法3: 导入到数据库
```bash
# 使用迁移脚本导入
python scripts/migration/import_sample_data.py \
  --assets tests/data/tara-sample/assets.json \
  --threats tests/data/tara-sample/threats.json \
  --measures tests/data/tara-sample/control_measures.json
```

## 数据格式说明

### 资产格式 (assets.json)
```json
{
  "id": "A-001",
  "name": "资产名称",
  "type": "ECU|存储|通信模块|接口|数据|服务",
  "category": "内部实体|外部接口|数据流",
  "description": "资产描述",
  "interfaces": ["接口类型1", "接口类型2"],
  "security_properties": {
    "confidentiality": "low|medium|high|critical",
    "integrity": "low|medium|high|critical",
    "availability": "low|medium|high|critical",
    "authenticity": true|false,
    "non_repudiation": true|false,
    "authorization": true|false
  },
  "criticality": "low|medium|high|critical"
}
```

### 威胁格式 (threats.json)
```json
{
  "id": "THR-001",
  "asset_id": "A-001",
  "threat_type": "S|T|R|I|D|E",
  "stride_category": "Spoofing|Tampering|Repudiation|Information Disclosure|Denial of Service|Elevation of Privilege",
  "name": "威胁名称",
  "description": "威胁描述",
  "attack_vector": "Network|Adjacent|Local|Physical",
  "attack_path": "攻击路径描述",
  "likelihood": {
    "expertise": 0-4,
    "elapsed_time": 0-4,
    "equipment": 0-4,
    "knowledge": 0-4,
    "window_of_opportunity": 0-4,
    "total": 0-20,
    "level": "Low|Medium|High"
  },
  "impact": {
    "safety": 0-4,
    "financial": 0-4,
    "operational": 0-4,
    "privacy": 0-4,
    "total": 0-4,
    "level": "Negligible|Minor|Moderate|Major|Severe"
  },
  "risk_level": "CAL-1|CAL-2|CAL-3|CAL-4"
}
```

### 控制措施格式 (control_measures.json)
```json
{
  "id": "CM-001",
  "threat_id": "THR-001",
  "name": "措施名称",
  "control_type": "preventive|detective|corrective",
  "category": "technical|organizational",
  "description": "措施描述",
  "implementation": "实施方法",
  "effectiveness": "low|medium|high",
  "iso21434_ref": "RQ-XX-XX"
}
```

## 扩展和自定义

### 添加新资产
1. 编辑 `assets.json` 或 `assets.csv`
2. 按照格式添加新资产记录
3. 确保资产ID唯一

### 添加新威胁
1. 编辑 `threats.json`
2. 关联到已有资产ID
3. 按STRIDE分类填写威胁类型
4. 评估攻击可行性和影响

### 添加控制措施
1. 编辑 `control_measures.json`
2. 关联到对应威胁ID
3. 参考ISO 21434附录填写参考条款

## 参考资料

- [ISO/SAE 21434:2021](https://www.iso.org/standard/70918.html) - 道路车辆网络安全工程
- [UN R155](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-155) - 网络安全管理系统
- [STRIDE威胁模型](https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [CVSS评分标准](https://www.first.org/cvss/)
