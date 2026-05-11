import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot run detail smoke', () => {
  test('renders events, evidence, diagnosis and remediation tabs', async ({ page }) => {
    await installOpsPilotMocks(page, {
      runId: 'run-detail-001',
      service: 'mysql',
      initialRunStatus: 'COMPLETED',
    });

    await page.goto('/runs/run-detail-001');

    await expect(page.getByRole('button', { name: '事件流' })).toBeVisible();
    await expect(page.getByText('Run started')).toBeVisible();

    await page.getByRole('button', { name: '证据' }).click();
    await expect(page.getByText('Retrieved logs data for mysql')).toBeVisible();

    await page.getByRole('button', { name: '诊断' }).click();
    await expect(page.getByText('近期部署变更导致依赖不兼容')).toBeVisible();

    await page.getByRole('button', { name: '方案' }).click();
    await expect(page.getByText('Proposed 1 remediation actions')).toBeVisible();
    await expect(page.getByText('restart')).toBeVisible();
  });
});
