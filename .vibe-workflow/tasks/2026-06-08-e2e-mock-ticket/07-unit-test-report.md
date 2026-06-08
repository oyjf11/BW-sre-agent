# 单元测试报告

## 命令

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q
```

## 结果

未完成。命令运行超过 3 分钟后仍未结束，输出停在已通过用例阶段；为了避免长期悬挂，已终止进程。该结果不能视为通过。

## Focused 回归

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_incidents_api.py app/tests/test_approvals_repo.py app/tests/test_resume_and_evidence.py app/tests/test_executor_preconditions.py -q
```

结果：`16 passed, 2 warnings in 9.62s`。

## Warnings

- `urllib3` 提示当前 Python ssl 模块使用 LibreSSL。
- SQLAlchemy `declarative_base()` 2.0 deprecation warning。
- Pydantic `validate_default` 元数据 warning。

