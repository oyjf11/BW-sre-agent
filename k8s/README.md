# OpsPilot 部署说明

## 部署前准备

### 1. 在 RDS 上建库

```sql
CREATE DATABASE opspilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 修改 backend/requirements.txt

追加：
```
aiomysql>=0.2.0
```

### 3. 替换占位符

以下文件里有 `<>` 占位符，替换为真实值：

| 文件 | 占位符 | 说明 |
|------|--------|------|
| `k8s/backend-deployment.yaml` | `<ACR_REGISTRY>` | 你的 ACR 仓库地址，如 `registry.cn-hangzhou.aliyuncs.com/your-ns` |
| `k8s/frontend-deployment.yaml` | `<ACR_REGISTRY>` | 同上 |
| `k8s/configmap.yaml` | `<YOUR_FRONTEND_DOMAIN>` | 前端域名，如 `opspilot.example.com` |
| `k8s/ingress.yaml` | `<YOUR_FRONTEND_DOMAIN>` / `<YOUR_BACKEND_DOMAIN>` | 前后端各自的域名 |

### 4. 在云效变量组配置 Secret

| 变量名 | 说明 |
|--------|------|
| `DATABASE_URL` | `mysql+aiomysql://user:pass@rds内网地址:3306/opspilot` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `MYSQL_HOST` | 业务 RDS 内网地址（取证用，只读） |
| `MYSQL_USER` | 业务 RDS 只读账号 |
| `MYSQL_PASSWORD` | 业务 RDS 只读密码 |
| `MYSQL_DB` | 业务数据库名，如 `hoo_ai` |

---

## 云效流水线步骤

### backend 流水线

```yaml
# 构建步骤
docker build -t registry.cn-shenzhen.aliyuncs.com/hoo-ops/opspilot-backend:${IMAGE_TAG} ./backend
docker push registry.cn-shenzhen.aliyuncs.com/hoo-ops/opspilot-backend:${IMAGE_TAG}

# 部署步骤（envsubst 注入 Secret 变量）
kubectl create namespace opspilot --dry-run=client -o yaml | kubectl apply -f -
envsubst < k8s/secret.yaml | kubectl apply -f -
kubectl apply -f k8s/configmap.yaml
# 更新镜像 tag
sed -i "s|opspilot-backend:latest|opspilot-backend:${IMAGE_TAG}|g" k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
```

### frontend 流水线

```yaml
# 构建步骤（VITE_API_URL 传入后端域名）
docker build \
  --build-arg VITE_API_URL=https://ops-api.yunhan100.com \
  -t registry.cn-shenzhen.aliyuncs.com/hoo-ops/opspilot-frontend:${IMAGE_TAG} \
  ./frontend
docker push registry.cn-shenzhen.aliyuncs.com/hoo-ops/opspilot-frontend:${IMAGE_TAG}

# 部署步骤
sed -i "s|opspilot-frontend:latest|opspilot-frontend:${IMAGE_TAG}|g" k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 首次部署后验证

```bash
# 查看 Pod 状态
kubectl get pods -n opspilot

# 查看后端日志（确认 alembic 迁移成功）
kubectl logs -n opspilot deployment/opspilot-backend

# 健康检查
curl https://ops-api.yunhan100.com/healthz
```

---

## 注意事项

- `k8s/secret.yaml` 是模板，**不要提交真实值**，真实值通过云效变量组在 CI 中 envsubst 注入
- 首次部署时后端启动会自动跑 `alembic upgrade head` 建表，日志里看到 `Alembic upgrade head completed` 表示成功
- SSE 流式输出依赖 Ingress 的 `proxy-buffering: off`，已在 `ingress.yaml` 配置
- 后端 `DATABASE_URL` 用 `aiomysql` 驱动，需确保 `requirements.txt` 里已加
