import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot approval smoke', () => {
  test('shows pending approval from run detail and approves it from approval detail', async ({
    page,
  }) => {
    const state = await installOpsPilotMocks(page, {
      runId: 'run-approval-001',
      approvalId: 'apr-approval-001',
      service: 'payment-service',
      env: 'prod',
      initialRunStatus: 'WAITING_HUMAN',
    });

    await page.goto(`/runs/${state.runId}`);

    await expect(page.getByText('等待人工')).toBeVisible();
    await expect(page.getByRole('link', { name: '前往审批' })).toBeVisible();
    await page.getByRole('link', { name: '前往审批' }).click();

    await expect(page).toHaveURL('/approvals');
    await expect(page.getByRole('heading', { name: '待审批列表' })).toBeVisible();
    await expect(page.getByText('payment-service')).toBeVisible();

    await page.getByRole('link', { name: /apr-appr/i }).click();
    await expect(page).toHaveURL(`/approvals/${state.approvalId}`);
    await expect(page.getByRole('heading', { name: '审批请求' })).toBeVisible();
    await page.getByRole('button', { name: '批准' }).click();

    await expect(page).toHaveURL('/approvals');

    await page.goto(`/runs/${state.runId}`);
    await expect(page.getByText('已完成')).toBeVisible();
  });
});
