"""
Enumerations
============

Enum definitions for TARA system.
"""

from enum import Enum, IntEnum


class ProjectStatus(IntEnum):
    """Project status enumeration."""
    
    DRAFT = 0        # 草稿
    IN_PROGRESS = 1  # 进行中
    COMPLETED = 2    # 已完成
    ARCHIVED = 3     # 已归档


class DocumentParseStatus(IntEnum):
    """Document parse status enumeration."""
    
    PENDING = 0     # 待解析
    PARSING = 1     # 解析中
    COMPLETED = 2   # 已完成
    FAILED = 3      # 解析失败


class AssetType(str, Enum):
    """Asset type enumeration."""
    
    ECU = "ECU"                      # 电子控制单元
    SENSOR = "Sensor"                # 传感器
    ACTUATOR = "Actuator"            # 执行器
    GATEWAY = "Gateway"              # 网关
    TBOX = "T-Box"                   # 远程信息处理器
    IVI = "IVI"                      # 车载信息娱乐系统
    ADAS = "ADAS"                    # 高级驾驶辅助系统
    BCM = "BCM"                      # 车身控制模块
    VCU = "VCU"                      # 整车控制器
    BMS = "BMS"                      # 电池管理系统
    OBD = "OBD"                      # 车载诊断接口
    HSM = "HSM"                      # 硬件安全模块
    NETWORK = "Network"              # 网络
    INTERFACE = "Interface"          # 接口
    DATA = "Data"                    # 数据
    SOFTWARE = "Software"            # 软件
    COMMUNICATION = "Communication"  # 通信
    EXTERNAL = "External"            # 外部系统


class AssetCategory(str, Enum):
    """Asset category enumeration."""
    
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    DATA = "Data"
    NETWORK = "Network"
    PHYSICAL = "Physical"
    PERSONNEL = "Personnel"


class ThreatType(str, Enum):
    """STRIDE threat type enumeration."""
    
    SPOOFING = "S"           # 欺骗 - 身份伪造
    TAMPERING = "T"          # 篡改 - 数据篡改
    REPUDIATION = "R"        # 否认 - 行为否认
    INFO_DISCLOSURE = "I"    # 信息泄露
    DENIAL_OF_SERVICE = "D"  # 拒绝服务
    ELEVATION = "E"          # 权限提升


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    
    NEGLIGIBLE = "negligible"  # 可忽略
    LOW = "low"                # 低
    MEDIUM = "medium"          # 中
    HIGH = "high"              # 高
    CRITICAL = "critical"      # 严重


class TreatmentDecision(str, Enum):
    """Risk treatment decision enumeration."""
    
    AVOID = "avoid"      # 规避风险
    REDUCE = "reduce"    # 降低风险
    SHARE = "share"      # 转移风险
    RETAIN = "retain"    # 接受风险


class FeasibilityRating(str, Enum):
    """Attack feasibility rating enumeration."""
    
    HIGH = "high"          # 高可行性
    MEDIUM = "medium"      # 中等可行性
    LOW = "low"            # 低可行性
    VERY_LOW = "very_low"  # 极低可行性


class ReportStatus(IntEnum):
    """Report generation status enumeration."""
    
    PENDING = 0     # 待生成
    GENERATING = 1  # 生成中
    COMPLETED = 2   # 已完成
    FAILED = 3      # 生成失败


class CAL(IntEnum):
    """Cybersecurity Assurance Level enumeration (ISO 21434)."""
    
    CAL1 = 1  # 基础安全保障
    CAL2 = 2  # 标准安全保障
    CAL3 = 3  # 高级安全保障
    CAL4 = 4  # 最高安全保障


class ControlType(str, Enum):
    """Control measure type enumeration."""
    
    PREVENTIVE = "preventive"  # 预防性
    DETECTIVE = "detective"    # 检测性
    CORRECTIVE = "corrective"  # 纠正性


class ControlCategory(str, Enum):
    """Control measure category enumeration."""
    
    TECHNICAL = "technical"      # 技术措施
    PROCEDURAL = "procedural"    # 流程措施
    PHYSICAL = "physical"        # 物理措施
