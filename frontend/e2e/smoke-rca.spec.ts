import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot RCA smoke', () => {
  test('opens RCA from the run detail page', async ({ page }) => {
    const state = await installOpsPilotMocks(page, {
      runId: 'run-rca-001',
      service: 'mysql',
      initialRunStatus: 'COMPLETED',
    });

    await page.goto(`/runs/${state.runId}`);
    await page.getByRole('link', { name: '查看根因分析' }).click();

    await expect(page).toHaveURL(`/runs/${state.runId}/rca`);
    await expect(page.getByRole('heading', { name: '根因分析' })).toBeVisible();
    await expect(page.getByText('近期部署变更导致依赖不兼容')).toBeVisible();
    await expect(page.getByText('回滚后恢复')).toBeVisible();
  });
});
