import { test as base, APIRequestContext } from '@playwright/test';

/**
 * Custom test fixture with API helpers
 */
export const test = base.extend<{
  api: APIRequestContext;
}>({
  api: async ({ request }, use) => {
    await use(request);
  },
});

export { expect } from '@playwright/test';
