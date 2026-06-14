# 3 天 Harness 入门实战清单

> ⏱ 阅读约 25 min

### 📌 本节学习目标

- 完成个人 Harness 系统搭建：注册中心 + 能力接入 + 执行调度 + 观测反馈
- 将已有 Skills 和 CLI 接入 Harness 统一管控，实现完整架构闭环
- 建立自动化评估体系，能量化衡量 AI 系统的执行质量
- 形成可复用的企业级 Harness 架构模板，具备快速复制推广能力

---

### 前提

完成 Skills + CLI 3 天实战清单，已有 2 个核心资产：

- Git 标准化提交流程 Skill + 配套 CLI 脚本
- 个人周报自动化生成 Skill + 配套 CLI 脚本

---

### 前置准备（提前 1 小时）

```bash
# 安装核心依赖
pip install context-harness python-dotenv python-json-logger

# 创建项目目录
mkdir my-ai-harness && cd my-ai-harness
mkdir registry skills cli_scripts logs
```

---

## Day 1：搭建 Harness 最小可用环境

> 学习时长：约 1.5 小时

### 任务 1：搭建 Harness 核心目录结构（30 分钟）

```text
my-ai-harness/
├── .env                     # 密钥管理（禁止上传 Git！）
├── harness_config.yaml      # Harness 核心配置
├── registry/                # 能力注册中心
│   ├── git_commit.yaml      # Git 提交 Skill 注册
│   └── weekly_report.yaml   # 周报 Skill 注册
├── skills/                  # Skills 业务逻辑
├── cli_scripts/             # CLI 执行脚本
├── logs/                    # 审计日志
└── main.py                  # Harness 统一调度入口
```

#### 编写 harness_config.yaml

```yaml
# Harness 核心配置
harness:
  version: "1.0.0"
  log_level: INFO
  log_dir: "./logs"

model:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.3

security:
  require_confirmation_for: ["high", "critical"]
  max_retries: 3
  timeout_seconds: 30

registry:
  path: "./registry"
```

### 任务 2：Skills 标准化注册（30 分钟）

#### 编写 registry/git_commit.yaml

```yaml
id: git-commit-standardize
name: Git 标准化提交流程
version: 1.0.0
description: 分析代码变更，生成符合 Angular 规范的提交信息，执行标准化提交和推送

applicable_when:
  - 代码变更需要提交时
not_applicable_when:
  - 合并分支或版本发布

risk_level: medium  # 推送操作为 high，读取为 low

input:
  repo_path: {type: string, description: "Git 仓库路径"}

output:
  commit_message: {type: string}
  push_result: {type: string}

execution:
  cli_script: "./cli_scripts/git_commit.sh"
  max_retries: 3
  timeout: 60
  confirmation_required_at: ["git_push"]  # 推送前需人工确认

permissions:
  allowed_paths: ["./"]  # 仅当前目录
  allowed_commands: ["git status", "git diff", "git add", "git commit", "git push"]
```

### 任务 3：编写 main.py 调度入口（20 分钟）

```python
# main.py - Harness 统一调度入口
import os
import yaml
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 配置结构化日志
logging.basicConfig(
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"logs/harness_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class HarnessCore:
    def __init__(self, config_path="harness_config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.skills = self._load_registry()
        logging.info(f"Harness 初始化成功，加载了 {len(self.skills)} 个 Skills")

    def _load_registry(self):
        registry = {}
        registry_path = self.config["registry"]["path"]
        for fname in os.listdir(registry_path):
            if fname.endswith(".yaml"):
                with open(f"{registry_path}/{fname}") as f:
                    skill = yaml.safe_load(f)
                    registry[skill["id"]] = skill
        return registry

    def dispatch(self, skill_id: str, inputs: dict) -> dict:
        if skill_id not in self.skills:
            raise ValueError(f"未知Skill: {skill_id}")

        skill = self.skills[skill_id]
        logging.info(f"开始执行Skill: {skill['name']}, inputs: {json.dumps(inputs)}")

        # 安全校验
        self._security_check(skill, inputs)

        # 执行
        result = self._execute_skill(skill, inputs)

        logging.info(f"Skill执行完成: {skill['name']}, success: {result.get('success')}")
        return result

    def _security_check(self, skill, inputs):
        risk = skill.get("risk_level", "low")
        if risk in ["high", "critical"]:
            print(f"\n⚠️ 高风险操作：{skill['name']} (风险等级: {risk})")
            confirm = input("请输入 'yes' 确认执行：")
            if confirm.lower() != "yes":
                raise PermissionError("用户拒绝执行")

    def _execute_skill(self, skill, inputs):
        import subprocess
        script = skill["execution"]["cli_script"]
        result = subprocess.run(
            ["bash", script], capture_output=True, text=True, timeout=60
        )
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}

if __name__ == "__main__":
    harness = HarnessCore()
    result = harness.dispatch("git-commit-standardize", {"repo_path": "."})
    print(result)
```

### Day 1 验收标准

- ✅ 成功搭建最小可用 Harness 环境，框架运行正常
- ✅ 完成 2 个核心 Skill 的标准化注册，元数据完整规范
- ✅ 能通过 Harness 统一调度入口执行 Skill 全流程

### Day 1 避坑小贴士 🛡️

1. **不要上来就搭复杂框架**：先从最小可用闭环入手，理解核心逻辑再逐步扩展
2. **元数据必须明确风险等级**：模糊不清的风险标注会导致安全校验失效，禁止使用「未知」
3. **路径和密钥用 .env 管理**：绝对禁止硬编码 API Key 到代码或配置文件
4. **先跑低风险场景**：先把 Git 提交（中风险）跑通，再碰周报生成（涉及个人数据），循序渐进

---

## Day 2：安全管控网关 + 全链路可观测体系

> 核心内容：白名单机制、权限最小化、人工确认节点、审计留痕、核心指标监控

### 安全管控中间件

```python
# security_gateway.py

COMMAND_WHITELIST = {
    "git": ["status", "diff", "add", "commit", "push", "pull", "log"],
    "ls": "_", "cat": "_", "find": "_", "echo": "_"
}

BLOCKED_COMMANDS = ["rm -rf", "dd ", "chmod 777", "sudo", "curl | bash"]

class SecurityGateway:
    def validate_command(self, command: str) -> bool:
        # 1. 黑名单检查
        for blocked in BLOCKED_COMMANDS:
            if blocked in command:
                raise SecurityError(f"危险命令被拦截: {blocked}")

        # 2. 白名单检查
        base_cmd = command.strip().split()[0]
        if base_cmd not in COMMAND_WHITELIST:
            raise SecurityError(f"命令 '{base_cmd}' 不在白名单中")

        return True

    def check_injection(self, param: str) -> bool:
        """防注入检查"""
        dangerous_patterns = [";", "&&", "||", "BACKTICK", "$(", ">", "<", "|"]
        for pattern in dangerous_patterns:
            if pattern in param:
                raise SecurityError(f"参数包含危险字符: PATTERN")
        return True
```

### 全链路观测体系

核心指标监控（每次任务执行后自动记录）：

| 指标 | 含义 | 告警阈值 |
|------|------|---------|
| 执行成功率 | 任务成功完成比例 | < 90% 触发告警 |
| 平均执行时长 | 任务执行耗时 | > 60s 触发告警 |
| Token 消耗 | 单任务 Token 用量 | > 5000 触发告警 |
| 异常拦截次数 | 安全网关拦截次数 | 任意次数记录 |
| 人工确认通过率 | 确认节点通过比例 | 统计分析 |

### Day 2 验收标准

- ✅ 非白名单命令 100% 被拦截
- ✅ 高风险操作强制触发人工确认
- ✅ 所有操作完整留痕，可通过 Trace ID 回溯

### Day 2 避坑小贴士 🛡️

1. **白名单要严格最小权限**：仅允许任务所需的具体命令，禁止使用通配符，避免规则被绕过
2. **人工确认仅加在高风险操作**：不要在只读操作上加确认节点，影响执行效率
3. **错误日志必须有完整上下文**：不要只打印「执行失败」，必须包含 Skill ID、命令、错误原因
4. **测试环境也要保持安全习惯**：不要为了方便关闭安全校验，养成严格习惯受益终生

---

## Day 3：多 Skill 编排 + 自动评估 + 项目交付

### 任务 1：「周报自动化全流程工作流」编排（40 分钟）

```python
# workflow.py - 多 Skill 工作流编排

class WorkflowEngine:
    def execute_weekly_report_workflow(self):
        trace_id = self._generate_trace_id()
        checkpoints = {}

        try:
            # Step 1: 拉取数据
            print("Step 1/4: 拉取多源数据...")
            data = self.harness.dispatch("data-collection", {})
            checkpoints["step1"] = data
            self._save_checkpoint(trace_id, checkpoints)

            # 检查点1：数据完整性校验
            if not data.get("git_commits"):
                print("⚠️ 未获取到Git提交记录，请手动输入本周工作...")

            # Step 2: 生成周报初稿
            print("Step 2/4: 生成周报初稿...")
            draft = self.harness.dispatch("weekly-report-writer", {
                "source_data": checkpoints["step1"]
            })
            checkpoints["step2"] = draft

            # 检查点2：人工预览确认
            print(f"\n📋 周报初稿：\n{draft['content']}")
            confirm = input("\n确认内容正确？(y/N): ")
            if confirm.lower() != 'y':
                print("已取消，请手动调整后重新执行")
                return

            # Step 3: 保存和分发
            print("Step 3/4: 保存周报...")
            save_result = self.harness.dispatch("file-save", {
                "content": draft['content'],
                "filename": f"weekly-report-{self._get_week()}.md"
            })

            # Step 4: 评估记录
            self._record_execution_metrics(trace_id, "success", checkpoints)
            print("✅ 周报自动化工作流执行完成！")

        except Exception as e:
            self._record_execution_metrics(trace_id, "failed", {"error": str(e)})
            raise
```

### 任务 2：自动化评估体系（40 分钟）

```python
# evaluator.py - 自动化评估

def evaluate_execution(task_result: dict, skill_config: dict) -> dict:
    """使用大模型自动评估执行效果"""
    from openai import OpenAI

    client = OpenAI()
    eval_prompt = f"""
    请评估以下AI任务的执行效果，返回JSON格式：

    任务类型：{skill_config['name']}
    执行结果：{task_result['output'][:500]}

    评估维度（0-100分）：
    1. 执行成功率：任务是否完整执行
    2. 输出合规性：是否符合预设输出规范
    3. 内容准确率：是否有幻觉或错误信息
    4. 执行效率：是否在合理时间内完成

    返回格式：
    {{"success_rate": 0-100, "compliance": 0-100, "accuracy": 0-100,
      "efficiency": 0-100, "overall": 0-100, "issues": ["问题1"], "suggestions": ["建议1"]}}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": eval_prompt}],
        response_format={"type": "json_object"}
    )

    evaluation = json.loads(response.choices[0].message.content)

    # Bad Case 自动收集
    if evaluation["overall"] < 60:
        log_bad_case(task_result, evaluation)

    return evaluation
```

### 任务 3：完整项目封装与交付（40 分钟）

1. **标准化优化**：完善代码注释、配置文件说明，规范目录结构，确保项目可移植、可复用
2. **安全加固**：清理硬编码密钥与敏感信息，完善 .gitignore，禁止 .env、日志文件上传到 Git
3. **项目交付**：将完整 Harness 系统（Skills + CLI + 配置 + 文档）整理成完整项目包，上传个人私有 GitHub 仓库（严禁公开仓库）
4. **制定迭代计划**：明确后续优化方向——新增业务 Skill、扩展 MCP 工具接入、优化调度引擎

### Day 3 项目最终验收标准

- ✅ 多 Skill 端到端工作流可正常执行，成功率 100%
- ✅ 自动化评估可正常量化评分，Bad Case 闭环机制生效
- ✅ 项目封装完整，代码规范，安全加固到位
- ✅ 能清晰讲解整个 Harness + Skills + CLI 架构设计

### Day 3 避坑小贴士 🛡️

1. **工作流不要过度复杂**：先把核心 4-5 步骤跑稳，再逐步扩展，避免流程断点过多
2. **评估不要只看「是否成功」**：重点关注输出质量、合规性、成本控制，这才是生产级核心
3. **项目必须上传私有仓库**：绝对不要上传公开仓库，避免泄露个人工作信息和敏感数据
4. **先上线再优化**：把当前系统用到日常工作中，在使用中持续优化，不要为了完善而迟迟不上线

---

## 安全红线总纲 🔴

1. **权限最小化**：任何场景，仅给 AI 完成任务所需最小权限，禁止 root 权限
2. **预览优先**：所有不可逆操作，必须先预览，100% 确认后再执行
3. **白名单机制**：仅允许预设的 CLI 命令执行
4. **全链路留痕**：所有操作记录不可篡改审计日志
5. **沙箱隔离**：企业级场景 CLI 必须在 Docker 沙箱中执行

---

## 后续进阶建议

1. 把 Harness 系统用到日常工作中，在使用中收集 Bad Case，持续优化
2. 扩展更多业务场景：月度总结、财务报销、数据报表自动化
3. 进阶学习企业级能力：MCP 协议扩展、多 Agent 协同、高可用部署

---

## 📝 本节小结

**3 天实战核心收获：**

1. 完整搭建 Harness 架构：注册中心 + Skills 接入 + CLI 接入 + 编排调度
2. 接入自动化评估体系：能量化监控 AI 系统执行质量
3. 形成可复用的个人 Harness 模板库，具备快速复制推广能力
