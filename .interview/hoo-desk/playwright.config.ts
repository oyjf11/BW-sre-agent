import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8081',
    trace: 'on',
    screenshot: 'only-on-failure',
  },
  reporter: [['json', { outputFile: '.vibe/runtime/pw-results.json' }], ['list']],
});
