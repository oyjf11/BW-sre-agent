import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot run detail realtime refresh', () => {
  test('appends SSE events, falls back to polling, and recovers automatically', async ({ page }) => {
    await installOpsPilotMocks(page, {
      runId: 'run-realtime-001',
      initialRunStatus: 'NEW',
    });
    await page.goto('/runs/run-realtime-001');

    await page.evaluate(() => {
      const sources = (window as any).__opspilotEventSources;
      sources[0].emit({
        event_id: 'evt-live',
        run_id: 'run-realtime-001',
        level: 'INFO',
        type: 'NODE_STARTED',
        message: 'Realtime event arrived',
        timestamp: '2026-06-02T10:00:02Z',
      });
    });
    await expect(page.getByText('Realtime event arrived')).toHaveCount(1);

    await page.evaluate(() => (window as any).__opspilotEventSources[0].fail());
    await expect(page.getByText(/已切换为自动刷新/)).toBeVisible();

    await page.waitForTimeout(5200);
    await page.evaluate(() => {
      const sources = (window as any).__opspilotEventSources;
      sources.at(-1).open();
    });
    await expect(page.getByText(/已切换为自动刷新/)).toHaveCount(0);
    await expect(page.getByText('Realtime event arrived')).toHaveCount(1);
  });

  for (const width of [1440, 1024, 768, 375]) {
    test(`does not overflow horizontally at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await installOpsPilotMocks(page, {
        runId: `run-responsive-${width}`,
        service: 'payment-service-with-an-intentionally-long-name',
        initialRunStatus: 'COMPLETED',
      });
      await page.goto(`/runs/run-responsive-${width}`);
      await expect(page.getByRole('button', { name: '事件流' })).toBeVisible();

      const overflow = await page.evaluate(() => ({
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
      }));
      expect(overflow.documentWidth).toBeLessThanOrEqual(overflow.viewportWidth);
    });
  }
});
