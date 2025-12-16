# 部署指南

本文档介绍 TARA System 的部署方式。

## 部署选项

| 环境 | 方式 | 适用场景 |
|------|------|----------|
| 开发 | Docker Compose | 本地开发测试 |
| 测试 | Docker Compose | CI/CD 测试 |
| 生产 | Kubernetes | 正式生产环境 |

## Docker Compose 部署

### 开发环境

```bash
# 启动所有服务
make docker-up

# 或分步启动
make docker-up-infra    # 基础设施
make docker-up-backend  # 后端服务
make docker-up-frontend # 前端
```

### 生产环境

```bash
# 使用生产配置
docker compose -f deploy/docker/docker-compose.yml \
               -f deploy/docker/docker-compose.prod.yml \
               up -d
```

## Kubernetes 部署

### 前提条件

- Kubernetes 集群 (1.24+)
- kubectl 配置完成
- Helm 3.0+ (可选)
- NGINX Ingress Controller

### 部署步骤

1. **创建命名空间**

```bash
kubectl apply -f deploy/k8s/base/namespace.yaml
```

2. **配置 Secrets**

```bash
# 创建 secrets (先修改 secrets.yaml 中的密码)
kubectl apply -f deploy/k8s/base/secrets.yaml
```

3. **部署基础设施**

```bash
# MySQL
kubectl apply -f deploy/k8s/base/infra/mysql.yaml

# Redis
kubectl apply -f deploy/k8s/base/infra/redis.yaml

# 其他数据库...
```

4. **部署后端服务**

```bash
# 使用 Kustomize
kubectl apply -k deploy/k8s/overlays/prod
```

5. **配置 Ingress**

```bash
kubectl apply -f deploy/k8s/base/ingress.yaml
```

### 使用 Kustomize

开发环境：
```bash
kubectl apply -k deploy/k8s/overlays/dev
```

生产环境：
```bash
kubectl apply -k deploy/k8s/overlays/prod
```

## AI 模型部署

### vLLM 部署

1. **使用 Docker**

```bash
docker run --gpus all -p 8000:8000 \
    -v /path/to/models:/models \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen2.5-7B-Instruct \
    --tensor-parallel-size 1
```

2. **Kubernetes 部署**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-service
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
            - --model
            - Qwen/Qwen2.5-7B-Instruct
          resources:
            limits:
              nvidia.com/gpu: 1
```

### GPU 资源配置

确保 Kubernetes 集群配置了 NVIDIA GPU 支持：

```bash
# 安装 NVIDIA device plugin
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
```

## 监控和日志

### Prometheus + Grafana

```bash
# 部署 Prometheus
kubectl apply -f deploy/monitoring/prometheus.yaml

# 部署 Grafana
kubectl apply -f deploy/monitoring/grafana.yaml
```

### 日志收集

使用 ELK Stack 或 Loki：

```bash
# 部署 Elasticsearch + Kibana
kubectl apply -f deploy/monitoring/elk.yaml
```

## 备份和恢复

### 数据库备份

```bash
# 自动备份 (添加到 crontab)
0 2 * * * /path/to/scripts/migration/backup.sh all

# 手动备份
./scripts/migration/backup.sh mysql
```

### 恢复

```bash
# 恢复 MySQL
gunzip -c backups/mysql_tara_db_20240101.sql.gz | mysql -u root -p tara_db
```

## 扩容

### 水平扩容

```bash
# 扩容后端服务
kubectl scale deployment project-service --replicas=3

# 或使用 HPA
kubectl apply -f deploy/k8s/base/hpa.yaml
```

### 垂直扩容

修改 Deployment 资源配置：

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## 安全配置

### TLS/SSL

1. 获取 SSL 证书
2. 创建 Kubernetes Secret
3. 配置 Ingress TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tara-ingress
spec:
  tls:
    - hosts:
        - tara.example.com
      secretName: tara-tls-secret
```

### 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tara-network-policy
spec:
  podSelector:
    matchLabels:
      app: tara
  policyTypes:
    - Ingress
    - Egress
```

## 健康检查

```bash
# 检查所有服务状态
./scripts/tools/health-check.sh

# Kubernetes 中查看 Pod 状态
kubectl get pods -n tara-system
kubectl describe pod <pod-name> -n tara-system
```

## 故障排除

### 查看日志

```bash
# Docker Compose
docker compose logs -f project-service

# Kubernetes
kubectl logs -f deployment/project-service -n tara-system
```

### 进入容器调试

```bash
# Docker
docker exec -it tara-project-service bash

# Kubernetes
kubectl exec -it <pod-name> -n tara-system -- bash
```

### 常见问题

1. **服务无法启动**: 检查环境变量和依赖服务
2. **数据库连接失败**: 检查网络配置和凭据
3. **内存不足**: 调整资源限制或扩容
4. **GPU 不可用**: 检查驱动和 device plugin
