"""
TARA Constants
==============

Constants for TARA analysis based on ISO/SAE 21434.
"""

from typing import Dict, List, Tuple

# ==================== STRIDE Threat Types ====================

STRIDE_TYPES: Dict[str, Dict[str, str]] = {
    "S": {
        "name": "Spoofing",
        "name_zh": "欺骗",
        "description": "身份伪造，冒充合法用户或系统",
        "violated_property": "Authentication",
    },
    "T": {
        "name": "Tampering",
        "name_zh": "篡改",
        "description": "恶意修改数据或代码",
        "violated_property": "Integrity",
    },
    "R": {
        "name": "Repudiation",
        "name_zh": "否认",
        "description": "否认已执行的操作",
        "violated_property": "Non-repudiation",
    },
    "I": {
        "name": "Information Disclosure",
        "name_zh": "信息泄露",
        "description": "未授权访问敏感信息",
        "violated_property": "Confidentiality",
    },
    "D": {
        "name": "Denial of Service",
        "name_zh": "拒绝服务",
        "description": "使系统或服务不可用",
        "violated_property": "Availability",
    },
    "E": {
        "name": "Elevation of Privilege",
        "name_zh": "权限提升",
        "description": "获取未授权的权限",
        "violated_property": "Authorization",
    },
}

# ==================== Impact Levels (ISO 21434 Table D.1) ====================

IMPACT_LEVELS: Dict[int, Dict[str, str]] = {
    0: {
        "level": "None",
        "level_zh": "无",
        "description": "无明显影响",
    },
    1: {
        "level": "Minor",
        "level_zh": "轻微",
        "description": "轻微影响",
    },
    2: {
        "level": "Moderate",
        "level_zh": "中等",
        "description": "中等影响",
    },
    3: {
        "level": "Major",
        "level_zh": "严重",
        "description": "严重影响",
    },
    4: {
        "level": "Severe",
        "level_zh": "致命",
        "description": "致命/灾难性影响",
    },
}

# Safety impact criteria
SAFETY_IMPACT_CRITERIA: Dict[int, str] = {
    0: "无安全影响",
    1: "轻微伤害风险",
    2: "可恢复的中等伤害风险",
    3: "严重伤害或不可恢复的伤害风险",
    4: "危及生命或致命伤害风险",
}

# Financial impact criteria
FINANCIAL_IMPACT_CRITERIA: Dict[int, str] = {
    0: "无财务影响",
    1: "损失 < ¥10,000",
    2: "损失 ¥10,000 - ¥100,000",
    3: "损失 ¥100,000 - ¥1,000,000",
    4: "损失 > ¥1,000,000",
}

# Operational impact criteria
OPERATIONAL_IMPACT_CRITERIA: Dict[int, str] = {
    0: "无运营影响",
    1: "轻微不便，可快速恢复",
    2: "中等影响，需要一定时间恢复",
    3: "严重影响，恢复困难",
    4: "完全中断，无法恢复",
}

# Privacy impact criteria
PRIVACY_IMPACT_CRITERIA: Dict[int, str] = {
    0: "无隐私影响",
    1: "非敏感个人信息泄露",
    2: "少量敏感个人信息泄露",
    3: "大量敏感个人信息泄露",
    4: "高度敏感信息泄露(如健康、位置跟踪)",
}

# ==================== Likelihood Levels ====================

LIKELIHOOD_LEVELS: Dict[int, Dict[str, str]] = {
    0: {
        "level": "None",
        "level_zh": "无",
        "description": "理论上可能但实际不太可能发生",
    },
    1: {
        "level": "Very Low",
        "level_zh": "极低",
        "description": "需要大量资源，极难实施",
    },
    2: {
        "level": "Low",
        "level_zh": "低",
        "description": "需要专业知识和资源，较难实施",
    },
    3: {
        "level": "Medium",
        "level_zh": "中",
        "description": "需要一定技能，可能被实施",
    },
    4: {
        "level": "High",
        "level_zh": "高",
        "description": "容易实施，可能被广泛利用",
    },
}

# ==================== Risk Matrix ====================

# Risk Matrix: RISK_MATRIX[impact][likelihood] = risk_level
RISK_MATRIX: List[List[str]] = [
    # Likelihood:  0      1      2        3        4
    ["negligible", "negligible", "negligible", "negligible", "low"],  # Impact 0
    ["negligible", "negligible", "low", "low", "medium"],  # Impact 1
    ["negligible", "low", "low", "medium", "high"],  # Impact 2
    ["negligible", "low", "medium", "high", "high"],  # Impact 3
    ["low", "medium", "high", "high", "critical"],  # Impact 4
]

# Risk level to numeric value mapping
RISK_LEVEL_VALUES: Dict[str, int] = {
    "negligible": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "critical": 5,
}

# ==================== Attack Potential (ISO 21434 Table D.2) ====================

# Expertise levels
ATTACK_POTENTIAL_EXPERTISE: Dict[int, Dict[str, str]] = {
    0: {
        "level": "Multiple Experts",
        "level_zh": "多名专家",
        "description": "需要多个领域的专家",
    },
    2: {"level": "Expert", "level_zh": "专家", "description": "需要特定领域专家"},
    4: {
        "level": "Proficient",
        "level_zh": "熟练者",
        "description": "需要熟练的技术人员",
    },
    6: {"level": "Layman", "level_zh": "普通人", "description": "普通人即可执行"},
    8: {
        "level": "No Expertise",
        "level_zh": "无需专业知识",
        "description": "无需任何专业知识",
    },
}

# Elapsed time
ATTACK_POTENTIAL_TIME: Dict[int, Dict[str, str]] = {
    0: {"level": "≥ 6 months", "level_zh": "≥ 6个月", "description": "需要6个月以上"},
    4: {"level": "< 6 months", "level_zh": "< 6个月", "description": "需要1-6个月"},
    7: {"level": "< 1 month", "level_zh": "< 1个月", "description": "需要1周-1个月"},
    10: {"level": "< 1 week", "level_zh": "< 1周", "description": "需要1天-1周"},
    15: {"level": "< 1 day", "level_zh": "< 1天", "description": "需要几小时-1天"},
    19: {"level": "< 1 hour", "level_zh": "< 1小时", "description": "需要不到1小时"},
}

# Equipment
ATTACK_POTENTIAL_EQUIPMENT: Dict[int, Dict[str, str]] = {
    0: {
        "level": "Multiple Bespoke",
        "level_zh": "多个定制设备",
        "description": "需要多个定制设备",
    },
    2: {"level": "Bespoke", "level_zh": "定制设备", "description": "需要定制/专用设备"},
    4: {
        "level": "Specialized",
        "level_zh": "专业设备",
        "description": "需要专业但可获取的设备",
    },
    6: {
        "level": "Standard",
        "level_zh": "标准设备",
        "description": "需要标准工具/设备",
    },
    10: {"level": "None", "level_zh": "无需设备", "description": "无需特殊设备"},
}

# Knowledge of target
ATTACK_POTENTIAL_KNOWLEDGE: Dict[int, Dict[str, str]] = {
    0: {
        "level": "Critical",
        "level_zh": "关键信息",
        "description": "需要关键/受限信息",
    },
    2: {"level": "Sensitive", "level_zh": "敏感信息", "description": "需要敏感信息"},
    4: {
        "level": "Restricted",
        "level_zh": "受限信息",
        "description": "需要受限但可获取的信息",
    },
    7: {"level": "Public", "level_zh": "公开信息", "description": "仅需公开信息"},
}

# Window of opportunity
ATTACK_POTENTIAL_WINDOW: Dict[int, Dict[str, str]] = {
    0: {"level": "None", "level_zh": "无", "description": "无攻击窗口"},
    1: {"level": "Very Small", "level_zh": "极小", "description": "极少的攻击机会"},
    4: {"level": "Small", "level_zh": "小", "description": "有限的攻击机会"},
    7: {"level": "Medium", "level_zh": "中等", "description": "中等攻击机会"},
    10: {"level": "Unlimited", "level_zh": "无限", "description": "随时可攻击"},
}

# Attack potential to feasibility mapping
ATTACK_POTENTIAL_TO_FEASIBILITY: List[Tuple[int, int, str]] = [
    (0, 9, "high"),  # 0-9: High feasibility
    (10, 17, "medium"),  # 10-17: Medium feasibility
    (18, 24, "low"),  # 18-24: Low feasibility
    (25, 100, "very_low"),  # 25+: Very low feasibility
]

# ==================== CAL Levels (Cybersecurity Assurance Level) ====================

CAL_LEVELS: Dict[int, Dict[str, str]] = {
    1: {
        "level": "CAL 1",
        "description": "基础安全保障",
        "description_en": "Basic cybersecurity assurance",
        "requirements": "基本的安全开发和测试流程",
    },
    2: {
        "level": "CAL 2",
        "description": "标准安全保障",
        "description_en": "Standard cybersecurity assurance",
        "requirements": "系统化的安全开发和验证流程",
    },
    3: {
        "level": "CAL 3",
        "description": "高级安全保障",
        "description_en": "Advanced cybersecurity assurance",
        "requirements": "严格的安全开发、测试和审计流程",
    },
    4: {
        "level": "CAL 4",
        "description": "最高安全保障",
        "description_en": "Highest cybersecurity assurance",
        "requirements": "最严格的安全开发、形式化验证和独立审计",
    },
}

# CAL determination based on risk level
RISK_LEVEL_TO_CAL: Dict[str, int] = {
    "negligible": 1,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

# ==================== Automotive Asset Types ====================

AUTOMOTIVE_ASSET_TYPES: List[Dict[str, str]] = [
    {"type": "ECU", "name_zh": "电子控制单元", "category": "Hardware"},
    {"type": "Sensor", "name_zh": "传感器", "category": "Hardware"},
    {"type": "Actuator", "name_zh": "执行器", "category": "Hardware"},
    {"type": "Gateway", "name_zh": "网关", "category": "Hardware"},
    {"type": "T-Box", "name_zh": "远程信息处理器", "category": "Hardware"},
    {"type": "IVI", "name_zh": "车载信息娱乐系统", "category": "Hardware"},
    {"type": "ADAS", "name_zh": "高级驾驶辅助系统", "category": "Hardware"},
    {"type": "BCM", "name_zh": "车身控制模块", "category": "Hardware"},
    {"type": "VCU", "name_zh": "整车控制器", "category": "Hardware"},
    {"type": "BMS", "name_zh": "电池管理系统", "category": "Hardware"},
    {"type": "OBD", "name_zh": "车载诊断接口", "category": "Interface"},
    {"type": "HSM", "name_zh": "硬件安全模块", "category": "Hardware"},
    {"type": "CAN", "name_zh": "CAN总线", "category": "Network"},
    {"type": "LIN", "name_zh": "LIN总线", "category": "Network"},
    {"type": "FlexRay", "name_zh": "FlexRay总线", "category": "Network"},
    {"type": "Ethernet", "name_zh": "车载以太网", "category": "Network"},
    {"type": "V2X", "name_zh": "V2X通信", "category": "Communication"},
    {"type": "Bluetooth", "name_zh": "蓝牙", "category": "Communication"},
    {"type": "Wi-Fi", "name_zh": "Wi-Fi", "category": "Communication"},
    {"type": "Cellular", "name_zh": "蜂窝网络", "category": "Communication"},
]

# ==================== Common Automotive Threats ====================

COMMON_AUTOMOTIVE_THREATS: List[Dict[str, str]] = [
    {
        "name": "CAN总线注入攻击",
        "type": "T",
        "description": "向CAN总线注入恶意消息，控制车辆功能",
    },
    {
        "name": "ECU固件篡改",
        "type": "T",
        "description": "篡改ECU固件，植入恶意代码",
    },
    {
        "name": "远程代码执行",
        "type": "E",
        "description": "利用漏洞在车辆系统上执行任意代码",
    },
    {
        "name": "中间人攻击",
        "type": "S",
        "description": "拦截和篡改车辆与云端的通信",
    },
    {
        "name": "拒绝服务攻击",
        "type": "D",
        "description": "使车辆系统或服务不可用",
    },
    {
        "name": "诊断接口滥用",
        "type": "E",
        "description": "通过OBD接口非法访问车辆系统",
    },
    {
        "name": "钥匙重放攻击",
        "type": "S",
        "description": "捕获并重放无线钥匙信号",
    },
    {
        "name": "用户数据泄露",
        "type": "I",
        "description": "未授权访问车辆用户隐私数据",
    },
]
