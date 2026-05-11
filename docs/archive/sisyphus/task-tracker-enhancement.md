# Task-Tracker 改进计划：状态持久化与故障恢复

## TL;DR

> 增强 task-tracker 的状态管理，实现多层备份、完整性校验、自动故障恢复，确保长任务中断或文件误删后能准确恢复进度。

**核心能力**：
1. **多层备份** - 主状态 + 备份 + 历史版本
2. **完整性校验** - 校验和 + JSON 验证
3. **自动恢复** - 检测损坏/丢失后自动重建
4. **增强审计** - 详细的状态变更日志

---

## Context

### 问题场景

| 场景 | 当前问题 | 影响 |
|------|---------|------|
| **长任务中断** | 重启后需手动检查进度 | 用户体验差，可能重复工作 |
| **状态文件误删** | 无法恢复，显示 "No tasks initialized" | 任务进度丢失 |
| **文件损坏** | JSON 解析失败，整个工具不可用 | 工作流中断 |
| **意外覆盖** | 写操作失败，状态丢失 | 数据丢失 |

### 根本原因

当前实现只有单一状态文件：
```python
# 只有一个文件，没有任何保护
STATE_FILE = ".task_state.json"
```

---

## Work Objectives

### 核心功能设计

#### 1. 多层状态存储

```
状态文件结构：
├── .task_state.json          # 主状态文件（当前）
├── .task_state.backup.json   # 自动备份（上一次保存的）
├── .task_state.v1.json       # 版本化备份
├── .task_state.v2.json       # ...
└── .task_state.lock          # 锁文件（防止并发）
```

**备份策略**：
- 每次保存前，先备份当前文件到 `.task_state.backup.json`
- 每 5 次保存，创建一个带时间戳的版本 `.task_state.v{n}.json`
- 保留最近 3 个版本

#### 2. 完整性校验

```python
class StateManager:
    def validate_state(self, state):
        """验证状态完整性"""
        errors = []
        
        # 1. 基础结构检查
        if "tasks" not in state:
            errors.append("missing 'tasks' key")
        
        # 2. 每个任务必须有必填字段
        required_fields = ["id", "name", "status"]
        for i, task in enumerate(state.get("tasks", [])):
            for field in required_fields:
                if field not in task:
                    errors.append(f"task {i}: missing '{field}'")
        
        # 3. 状态值必须是有效值
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        for i, task in enumerate(state.get("tasks", [])):
            if task.get("status") not in valid_statuses:
                errors.append(f"task {i}: invalid status '{task.get('status')}'")
        
        return len(errors) == 0, errors
```

#### 3. 自动故障恢复

```python
class RecoveryManager:
    """故障恢复管理器"""
    
    def recover(self):
        """自动恢复状态"""
        sources = [
            self.load_primary,      # 1. 尝试主文件
            self.load_backup,       # 2. 尝试备份
            self.load_latest_version, # 3. 尝试最新版本
            self.rebuild_from_checklist, # 4. 从清单重建
        ]
        
        for source in sources:
            state = source()
            if state and self.validate_state(state):
                return state, f"Recovered from {source.__name__}"
        
        # 所有来源都失败
        return None, "Recovery failed - please run 'init'"
```

#### 4. 增强的状态审计

```python
# 每个任务记录详细历史
task = {
    "id": 1,
    "name": "实现登录功能",
    "status": "in_progress",
    "created_at": "2026-03-07T10:00:00",
    "updated_at": "2026-03-07T12:00:00",
    "completed_at": None,
    "history": [
        {"timestamp": "2026-03-07T10:00:00", "action": "created", "from": None, "to": "pending"},
        {"timestamp": "2026-03-07T10:05:00", "action": "started", "from": "pending", "to": "in_progress"},
    ],
    "note": "等待后端API就绪",  # 用户可以添加注释
}
```

#### 5. 锁机制（防止并发冲突）

```python
import fcntl

def acquire_lock():
    lock_file = Path(".task_state.lock")
    lock_file.touch()
    with open(lock_file, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield
        fcntl.flock(f, fcntl.LOCK_UN)
```

---

## 新增命令设计

| 命令 | 功能 |
|------|------|
| `repair` | 手动触发状态修复 |
| `history <task>` | 查看任务状态变更历史 |
| `export` | 导出状态为不同格式 |
| `lock` | 查看/管理锁状态 |

---

## Execution Strategy

### 文件修改

| 文件 | 修改内容 |
|------|---------|
| `.opencode/skills/task-tracker/scripts/task_tracker.py` | 全面重构，新增状态管理类 |

### 实现步骤

#### Wave 1: 核心状态管理
- [ ] 1. 创建 StateManager 类 - 负责加载/保存/验证
- [ ] 2. 创建 BackupManager 类 - 负责多层备份
- [ ] 3. 创建 RecoveryManager 类 - 负责故障恢复
- [ ] 4. 实现锁机制

#### Wave 2: 命令更新
- [ ] 5. 重构 load_state/save_state 使用新管理器
- [ ] 6. 添加 repair 命令
- [ ] 7. 添加 history 命令
- [ ] 8. 启动时自动检测和恢复

#### Wave 3: 审计增强
- [ ] 9. 添加任务历史记录
- [ ] 10. 添加注释功能
- [ ] 11. 添加时间戳追踪

---

## 故障场景测试

### 场景1：文件误删
```bash
# 1. 正常初始化
python task_tracker.py init

# 2. 删除状态文件
rm .task_state.json

# 3. 再次运行任何命令
python task_tracker.py status

# 期望输出：
# ✓ 检测到状态文件丢失
# ✓ 从备份恢复成功
# Progress: 0/5 completed (0%)
```

### 场景2：文件损坏
```bash
# 1. 手动破坏 JSON
echo "{ broken json" > .task_state.json

# 2. 运行命令
python task_tracker.py status

# 期望输出：
# ⚠ 检测到状态文件损坏
# ✓ 从备份恢复成功
# Progress: 2/5 completed (40%)
```

### 场景3：中断恢复
```bash
# 1. 查看当前进度
python task_tracker.py status
# In Progress: 实现登录功能

# 2. 模拟中断（关闭终端）

# 3. 重新打开终端
python task_tracker.py next

# 期望输出：
# Current task (in progress):
#   实现登录功能
#   Criteria: 用户能登录系统
```

---

## Verification

### 测试用例

1. **test_recovery_from_backup**
   - 备份存在，主文件不存在 → 从备份恢复

2. **test_recovery_from_corrupt**
   - 主文件 JSON 损坏 → 从备份恢复

3. **test_recovery_from_checklist**
   - 所有状态文件丢失 → 从清单重建

4. **test_concurrent_access**
   - 两个进程同时操作 → 第二个被锁阻塞

5. **test_history_tracking**
   - 状态变更 → 历史记录正确

---

## Commit Strategy

- `feat(task-tracker): add multi-layer state backup`
- `feat(task-tracker): add integrity validation`
- `feat(task-tracker): add automatic recovery`
- `feat(task-tracker): add lock mechanism`
- `feat(task-tracker): add audit history`

---

## Success Criteria

- [ ] 删除状态文件后能自动恢复
- [ ] JSON 损坏后能自动恢复
- [ ] 启动时自动检测并恢复
- [ ] 记录完整的状态变更历史
- [ ] 防止并发写入冲突
- [ ] 文档更新完整
