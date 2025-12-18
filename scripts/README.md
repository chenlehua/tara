# TARA System 脚本

本目录包含系统安装、配置、迁移和维护脚本。

## 目录结构

```
scripts/
├── setup/              # 环境安装脚本
│   ├── install.sh      # 完整安装
│   ├── install-dev.sh  # 开发环境安装
│   └── init-db.sh      # 数据库初始化
├── migration/          # 数据迁移脚本
│   ├── migrate.py      # 数据库迁移工具
│   └── backup.sh       # 备份脚本
└── tools/              # 工具脚本
    ├── generate-key.py # 密钥生成
    ├── health-check.sh # 健康检查
    └── cleanup.sh      # 清理脚本
```

## 使用方法

### 安装
```bash
# 完整安装
./scripts/setup/install.sh

# 开发环境
./scripts/setup/install-dev.sh
```

### 数据库
```bash
# 初始化数据库
./scripts/setup/init-db.sh

# 迁移数据库
python scripts/migration/migrate.py upgrade
```

### 维护
```bash
# 健康检查
./scripts/tools/health-check.sh

# 清理临时文件
./scripts/tools/cleanup.sh
```
