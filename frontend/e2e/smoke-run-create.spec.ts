import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot run creation smoke', () => {
  test('creates a manual incident and opens the run detail page', async ({ page }) => {
    const state = await installOpsPilotMocks(page, {
      runId: 'run-create-001',
      service: 'mysql',
      env: 'prod',
      initialRunStatus: 'COMPLETED',
    });

    await page.goto('/runs/new');

    await expect(page.getByRole('heading', { name: '创建事件处理' })).toBeVisible();
    await page.getByPlaceholder('服务降级').fill('MySQL 连接错误率升高');
    await page.getByPlaceholder('api-gateway').first().fill(state.service);
    await page.getByPlaceholder('描述事件...').fill('发布后部分请求无法访问数据库');
    await page.getByRole('button', { name: '创建事件处理' }).click();

    await expect(page).toHaveURL(`/runs/${state.runId}`);
    await expect(page.getByText(state.service)).toBeVisible();
    await expect(page.getByText('已完成')).toBeVisible();
    await expect(page.getByRole('button', { name: '事件流' })).toBeVisible();
    await expect(page.getByRole('button', { name: '证据' })).toBeVisible();
    await expect(page.getByRole('button', { name: '诊断' })).toBeVisible();
    await expect(page.getByRole('button', { name: '方案' })).toBeVisible();
  });
});
