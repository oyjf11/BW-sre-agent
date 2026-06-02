# OpsPilot 工程启动指南

## 前置条件

| 依赖 | 最低版本 | 验证命令 |
|------|---------|---------|
| Python | 3.9+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

## 一、一键启动（推荐）

```bash
# 在项目根目录执行
chmod +x start-dev.sh
./start-dev.sh
```

该脚本会自动检测可用端口、检查依赖，并以 watch 模式启动前后端。
按 `Ctrl+C` 即可同时停止两个服务。

## 二、手动分步启动

### 1. 后端

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（首次或依赖变更后）
pip install -r requirements.txt

# 启动后端（默认监听 127.0.0.1:8000）
uvicorn app.main:app --reload --port 8000
```

### 2. 前端

```bash
cd frontend

# 安装依赖（首次或依赖变更后）
npm install

# 启动前端（默认监听 http://localhost:5173）
npm run dev
```

## 三、环境配置

### 后端环境变量 (`backend/.env`)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM 提供商 | `minimax` |
| `TOOL_ADAPTER_MODE` | 工具适配器模式 | `mock` |

可选 LLM 提供商：
- `deepseek`：需设置 `DEEPSEEK_API_KEY` + `DEEPSEEK_MODEL`
- `openai`：需设置 `OPENAI_API_KEY` + `OPENAI_MODEL`
- `minimax`：需设置 `MINIMAX_API_KEY` + `MINIMAX_GROUP_ID`

`TOOL_ADAPTER_MODE` 说明：
- `mock`：使用 mock 适配器返回仿真数据，适合本地开发
- `real`：使用生产适配器（MySQL、K8s、CMS、SLB、OSS），需要额外配置

### 前端环境变量

前端通过 `VITE_API_URL` 指定后端地址，默认 `http://localhost:8000`：

```bash
# 如需自定义后端地址，在 frontend/ 目录创建 .env 文件
echo "VITE_API_URL=http://localhost:8000" > frontend/.env
```

## 四、验证服务

### 后端健康检查

```bash
curl http://127.0.0.1:8000/healthz
# 预期输出：{"status": "ok"}
```

### 后端 API 文档

浏览器访问：
- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

### 前端页面

浏览器访问：http://localhost:5173

## 五、常用脚本速查

```bash
# 后端测试
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q

# 前端测试
cd frontend && npx vitest run

# 前端类型检查
cd frontend && npx tsc --noEmit

# 前端代码检查
cd frontend && npm run lint

# 查看 run 状态
curl -s http://127.0.0.1:8000/incidents/runs/{run_id} | python3 -m json.tool

# 创建工单（手工）
curl -s -X POST http://127.0.0.1:8000/incidents/runs \
  -H "Content-Type: application/json" \
  -d '{"ticket":{"ticket_id":"INC-001","title":"测试工单","description":"","service":"test","env":"staging","severity":"P3","source":"manual"}}' \
  | python3 -m json.tool
```

## 六、常见问题

### Q: 启动报 `uvicorn: command not found`
先激活 venv：`cd backend && source venv/bin/activate`

### Q: 端口被占用
默认后端 8000，前端 5173。使用 `start-dev.sh` 可自动寻找可用端口。  
手动指定端口：`--port 8001`（后端）或 `npm run dev -- --port 5174`（前端）。

### Q: 前端请求后端报 CORS 错误
确认 `VITE_API_URL` 指向正确的后端地址。

### Q: `frontend/node_modules` 缺失
执行 `cd frontend && npm install`

### Q: 后端报 LLM 调用失败
检查 `backend/.env` 中的 `LLM_PROVIDER` 和对应 API Key 配置。  
dev 环境不强制校验 key，但 LLM 调用会失败。

### Q: macOS 下 `lsof` 不可用
`start-dev.sh` 中端口检测依赖 `lsof`，macOS 自带。若缺失请 `brew install lsof`。
