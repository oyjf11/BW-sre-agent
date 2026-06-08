import { Framework, Profile, ProfileSchema } from './contracts';

const UI_DEFAULTS: Record<Framework, { toast_selector: string; ready_log: string }> = {
  vue2: { toast_selector: '.el-message', ready_log: 'Compiled successfully' },
  vue3: { toast_selector: '.el-message', ready_log: 'ready in' },
  'react16-minus': { toast_selector: '.ant-message', ready_log: 'Compiled successfully' },
  'react16-plus': { toast_selector: '.ant-message', ready_log: 'Compiled successfully' },
};

export function buildProfile(framework: Framework, project: string): Profile {
  const ui = UI_DEFAULTS[framework];
  const profile: Profile = {
    project,
    framework,
    dev: {
      command: 'npm run dev',
      ready_log: ui.ready_log,
      base_url: 'http://localhost:8080',
      timeout_ms: 180000,
    },
    ui: {
      adapter: framework,
      toast_selector: ui.toast_selector,
      input_strategy: 'placeholder',
    },
    acceptance_dir: '.vibe/specs/acceptance',
    e2e_out_dir: 'e2e',
  };
  return ProfileSchema.parse(profile);
}
