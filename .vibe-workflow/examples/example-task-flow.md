# 示例：登录页增加验证码校验

## 推荐命令顺序

```text
/vibe-clarify-requirements 登录失败 3 次后展示验证码，并在登录成功后重置失败次数
/vibe-design-requirements
/vibe-detailed-design
/vibe-frontend-design
/vibe-backend-design
/vibe-implement-code Step 1: 后端失败次数记录与验证码状态接口
/vibe-unit-tests
/vibe-implement-code Step 2: 前端登录页验证码展示与提交
/vibe-unit-tests
/vibe-integration-tests
/vibe-e2e-playwright
/vibe-review-diff
/vibe-learn
```

## 切片原则

1. 后端能力先闭环。
2. 前端 UI 再接入。
3. 单元测试覆盖规则。
4. 集成测试覆盖 API + DB。
5. E2E 覆盖真实登录路径。
