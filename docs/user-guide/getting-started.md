# 快速开始

本指南帮助您快速开始使用 TARA System 进行威胁分析与风险评估。

## 系统要求

### 最低配置
- CPU: 8 核心
- 内存: 32 GB
- 存储: 100 GB SSD
- GPU: NVIDIA GPU (16GB+ VRAM) - 用于 AI 模型

### 推荐配置
- CPU: 16+ 核心
- 内存: 64 GB
- 存储: 500 GB NVMe SSD
- GPU: NVIDIA A100 40GB 或同等

## 安装

### 使用 Docker Compose (推荐)

1. 克隆仓库
```bash
git clone https://github.com/your-org/tara-system.git
cd tara-system
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库密码等
```

3. 启动服务
```bash
# 启动基础设施
make docker-up-infra

# 初始化数据库
make db-init

# 启动后端服务
make docker-up-backend

# 启动前端
make docker-up-frontend
```

4. 访问系统
打开浏览器访问 http://localhost:3000

### 本地开发安装

1. 安装依赖
```bash
make install
```

2. 启动开发服务器
```bash
# 终端 1: 后端服务
make backend-dev

# 终端 2: 前端服务
make frontend-dev
```

## 第一个项目

### 1. 创建项目

登录系统后，点击「新建项目」：

- **项目名称**: 输入项目名称，如 "新能源汽车TARA分析"
- **车辆类型**: 选择 BEV/HEV/ICE/FCEV
- **参考标准**: 选择 ISO/SAE 21434 或 UN R155
- **项目描述**: 简要描述项目范围

### 2. 上传文档

进入项目后，在「文档」标签页：

1. 点击「上传文档」
2. 选择技术文档（支持 PDF、Word、Excel）
3. 等待文档解析完成

系统会自动：
- 识别文档结构
- 提取技术内容
- 识别系统组件

### 3. 资产识别

在「资产」标签页：

1. 点击「AI 识别资产」
2. 系统自动从文档中识别资产
3. 审核并确认识别结果
4. 手动添加/修改资产信息

资产类型包括：
- ECU (电子控制单元)
- 网关
- 通信总线
- 传感器/执行器
- 外部接口

### 4. 威胁分析

在「威胁」标签页：

1. 点击「STRIDE 分析」
2. 选择要分析的资产
3. 系统自动识别威胁
4. 审核威胁场景
5. 配置攻击路径

STRIDE 类型：
- **S**poofing (欺骗)
- **T**ampering (篡改)
- **R**epudiation (否认)
- **I**nformation Disclosure (信息泄露)
- **D**enial of Service (拒绝服务)
- **E**levation of Privilege (权限提升)

### 5. 风险评估

在「风险」标签页：

1. 查看风险矩阵
2. 评估每个威胁的影响和可能性
3. 系统自动计算风险等级
4. 选择风险处置策略

风险等级：
- 🔴 严重 (Critical)
- 🟠 高 (High)
- 🔵 中 (Medium)
- 🟢 低 (Low)
- ⚪ 可忽略 (Negligible)

### 6. 生成报告

在「报告」标签页：

1. 点击「生成报告」
2. 选择报告模板：
   - ISO/SAE 21434 标准模板
   - UN R155 合规模板
   - 简洁模板
3. 选择导出格式（PDF/Word）
4. 等待报告生成
5. 下载报告

## 常见操作

### AI 对话助手

点击右下角的对话按钮，与 AI 助手交流：

- "分析 OBD 接口的安全风险"
- "推荐针对 CAN 总线注入的控制措施"
- "解释 STRIDE 威胁模型"

### 资产图谱

在「资产图谱」页面：

- 查看资产关系可视化
- 点击节点查看详情
- 识别信任边界
- 分析数据流

### 批量操作

支持批量操作：

- 批量导入资产
- 批量分析威胁
- 批量评估风险

## 下一步

- [项目管理详解](project-management.md)
- [TARA 工作流详解](tara-workflow.md)
- [报告生成详解](report-generation.md)

## 获取帮助

- 查看 [常见问题](faq.md)
- 提交 [Issue](https://github.com/your-org/tara-system/issues)
- 联系技术支持
