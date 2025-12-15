-- ===========================================
-- TARA System Database Initialization
-- ===========================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS tara_db 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE tara_db;

-- ===========================================
-- Projects Table
-- ===========================================
CREATE TABLE IF NOT EXISTS projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '项目名称',
    description TEXT COMMENT '项目描述',
    vehicle_type VARCHAR(50) COMMENT '车辆类型',
    vehicle_model VARCHAR(100) COMMENT '车型',
    vehicle_year VARCHAR(10) COMMENT '年份',
    standard VARCHAR(50) DEFAULT 'ISO/SAE 21434' COMMENT '参考标准',
    scope TEXT COMMENT '分析范围',
    status TINYINT DEFAULT 0 COMMENT '状态: 0-草稿, 1-进行中, 2-已完成, 3-已归档',
    owner VARCHAR(100) COMMENT '负责人',
    team JSON COMMENT '项目团队',
    config JSON COMMENT '项目配置',
    tags JSON COMMENT '标签',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';

-- ===========================================
-- Documents Table
-- ===========================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL COMMENT '项目ID',
    filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '存储路径',
    file_size BIGINT COMMENT '文件大小(bytes)',
    file_type VARCHAR(50) COMMENT 'MIME类型',
    file_extension VARCHAR(20) COMMENT '文件扩展名',
    doc_type VARCHAR(50) COMMENT '文档类型',
    doc_category VARCHAR(50) COMMENT '文档分类',
    parse_status TINYINT DEFAULT 0 COMMENT '解析状态: 0-待解析, 1-解析中, 2-已完成, 3-失败',
    parse_progress TINYINT DEFAULT 0 COMMENT '解析进度',
    parse_error TEXT COMMENT '解析错误信息',
    title VARCHAR(255) COMMENT '文档标题',
    content LONGTEXT COMMENT '文档文本内容',
    structure JSON COMMENT '文档结构',
    metadata JSON COMMENT '文档元数据',
    ocr_result JSON COMMENT 'OCR识别结果',
    page_count SMALLINT COMMENT '页数',
    embedding_status TINYINT DEFAULT 0 COMMENT '向量化状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_parse_status (parse_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档表';

-- ===========================================
-- Assets Table
-- ===========================================
CREATE TABLE IF NOT EXISTS assets (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL COMMENT '项目ID',
    parent_id BIGINT COMMENT '父资产ID',
    name VARCHAR(200) NOT NULL COMMENT '资产名称',
    asset_type VARCHAR(50) NOT NULL COMMENT '资产类型',
    category VARCHAR(50) COMMENT '资产分类',
    description TEXT COMMENT '资产描述',
    version VARCHAR(50) COMMENT '版本',
    vendor VARCHAR(100) COMMENT '供应商',
    model_number VARCHAR(100) COMMENT '型号',
    security_attrs JSON COMMENT '安全属性',
    interfaces JSON COMMENT '接口列表',
    data_types JSON COMMENT '处理的数据类型',
    location VARCHAR(200) COMMENT '物理位置',
    zone VARCHAR(50) COMMENT '安全区域',
    trust_boundary VARCHAR(50) COMMENT '信任边界',
    is_external TINYINT DEFAULT 0 COMMENT '是否外部资产',
    criticality VARCHAR(20) COMMENT '关键性',
    status TINYINT DEFAULT 1 COMMENT '状态',
    source VARCHAR(50) DEFAULT 'manual' COMMENT '来源',
    source_doc_id BIGINT COMMENT '来源文档ID',
    neo4j_node_id VARCHAR(100) COMMENT 'Neo4j节点ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES assets(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_asset_type (asset_type),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资产表';

-- ===========================================
-- Damage Scenarios Table
-- ===========================================
CREATE TABLE IF NOT EXISTS damage_scenarios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asset_id BIGINT NOT NULL COMMENT '资产ID',
    name VARCHAR(200) NOT NULL COMMENT '损害场景名称',
    description TEXT COMMENT '场景描述',
    safety_impact TINYINT DEFAULT 0 COMMENT '安全影响: 0-4',
    financial_impact TINYINT DEFAULT 0 COMMENT '财务影响: 0-4',
    operational_impact TINYINT DEFAULT 0 COMMENT '运营影响: 0-4',
    privacy_impact TINYINT DEFAULT 0 COMMENT '隐私影响: 0-4',
    impact_level TINYINT COMMENT '综合影响等级',
    impact_justification TEXT COMMENT '影响评估说明',
    stakeholders JSON COMMENT '受影响的利益相关者',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    INDEX idx_asset_id (asset_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='损害场景表';

-- ===========================================
-- Threat Risks Table
-- ===========================================
CREATE TABLE IF NOT EXISTS threat_risks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL COMMENT '项目ID',
    asset_id BIGINT NOT NULL COMMENT '资产ID',
    damage_scenario_id BIGINT COMMENT '损害场景ID',
    threat_name VARCHAR(200) NOT NULL COMMENT '威胁名称',
    threat_type VARCHAR(20) COMMENT '威胁类型(STRIDE)',
    threat_desc TEXT COMMENT '威胁描述',
    attack_vector TEXT COMMENT '攻击向量',
    attack_surface VARCHAR(100) COMMENT '攻击面',
    threat_source VARCHAR(50) COMMENT '威胁源',
    threat_agent VARCHAR(100) COMMENT '威胁主体',
    safety_impact TINYINT DEFAULT 0 COMMENT '安全影响',
    financial_impact TINYINT DEFAULT 0 COMMENT '财务影响',
    operational_impact TINYINT DEFAULT 0 COMMENT '运营影响',
    privacy_impact TINYINT DEFAULT 0 COMMENT '隐私影响',
    impact_level TINYINT COMMENT '综合影响等级',
    likelihood TINYINT COMMENT '可能性等级: 0-4',
    risk_value TINYINT COMMENT '风险值',
    risk_level VARCHAR(20) COMMENT '风险等级',
    treatment VARCHAR(50) COMMENT '处置决策',
    treatment_desc TEXT COMMENT '处置说明',
    residual_risk TINYINT COMMENT '残余风险',
    cal TINYINT COMMENT '网络安全保障等级',
    verification_status TINYINT DEFAULT 0 COMMENT '验证状态',
    verified_by VARCHAR(100) COMMENT '验证人',
    source VARCHAR(50) DEFAULT 'manual' COMMENT '来源',
    cwe_ids JSON COMMENT 'CWE ID列表',
    capec_ids JSON COMMENT 'CAPEC ID列表',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    FOREIGN KEY (damage_scenario_id) REFERENCES damage_scenarios(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_asset_id (asset_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_threat_type (threat_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='威胁风险表';

-- ===========================================
-- Attack Paths Table
-- ===========================================
CREATE TABLE IF NOT EXISTS attack_paths (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    threat_risk_id BIGINT NOT NULL COMMENT '威胁风险ID',
    name VARCHAR(200) NOT NULL COMMENT '攻击路径名称',
    description TEXT COMMENT '路径描述',
    steps JSON COMMENT '攻击步骤',
    expertise TINYINT DEFAULT 0 COMMENT '专业知识: 0-8',
    elapsed_time TINYINT DEFAULT 0 COMMENT '时间: 0-19',
    equipment TINYINT DEFAULT 0 COMMENT '设备: 0-10',
    knowledge TINYINT DEFAULT 0 COMMENT '信息获取: 0-7',
    window_of_opportunity TINYINT DEFAULT 0 COMMENT '机会窗口: 0-10',
    attack_potential TINYINT COMMENT '攻击潜力值',
    feasibility_rating VARCHAR(20) COMMENT '攻击可行性',
    prerequisites JSON COMMENT '前置条件',
    attack_techniques JSON COMMENT 'ATT&CK技术',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (threat_risk_id) REFERENCES threat_risks(id) ON DELETE CASCADE,
    INDEX idx_threat_risk_id (threat_risk_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='攻击路径表';

-- ===========================================
-- Control Measures Table
-- ===========================================
CREATE TABLE IF NOT EXISTS control_measures (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    attack_path_id BIGINT NOT NULL COMMENT '攻击路径ID',
    name VARCHAR(200) NOT NULL COMMENT '控制措施名称',
    control_type VARCHAR(50) COMMENT '类型',
    category VARCHAR(50) COMMENT '分类',
    description TEXT COMMENT '措施描述',
    implementation TEXT COMMENT '实施方式',
    implementation_status TINYINT DEFAULT 0 COMMENT '实施状态',
    effectiveness VARCHAR(20) COMMENT '有效性',
    residual_risk_reduction TINYINT COMMENT '残余风险降低量',
    cost_estimate VARCHAR(50) COMMENT '成本估算',
    implementation_effort VARCHAR(50) COMMENT '实施工作量',
    iso21434_ref VARCHAR(50) COMMENT 'ISO 21434参考条款',
    verification_method TEXT COMMENT '验证方法',
    verification_status TINYINT DEFAULT 0 COMMENT '验证状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (attack_path_id) REFERENCES attack_paths(id) ON DELETE CASCADE,
    INDEX idx_attack_path_id (attack_path_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='控制措施表';

-- ===========================================
-- Reports Table
-- ===========================================
CREATE TABLE IF NOT EXISTS reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL COMMENT '项目ID',
    name VARCHAR(200) NOT NULL COMMENT '报告名称',
    report_type VARCHAR(50) DEFAULT 'tara' COMMENT '报告类型',
    description TEXT COMMENT '报告描述',
    template VARCHAR(100) COMMENT '使用的模板',
    template_version VARCHAR(20) COMMENT '模板版本',
    content JSON COMMENT '报告内容',
    sections JSON COMMENT '报告章节',
    status TINYINT DEFAULT 0 COMMENT '状态',
    progress TINYINT DEFAULT 0 COMMENT '进度',
    error_message TEXT COMMENT '错误信息',
    file_path VARCHAR(500) COMMENT '文件存储路径',
    file_format VARCHAR(20) COMMENT '文件格式',
    file_size BIGINT COMMENT '文件大小',
    version VARCHAR(20) DEFAULT '1.0' COMMENT '报告版本',
    author VARCHAR(100) COMMENT '作者',
    reviewer VARCHAR(100) COMMENT '审核人',
    review_status TINYINT DEFAULT 0 COMMENT '审核状态',
    statistics JSON COMMENT '报告统计数据',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告表';
