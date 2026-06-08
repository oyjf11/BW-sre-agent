import { SelectorAdapter } from './types';

export const vue2Adapter: SelectorAdapter = {
  framework: 'vue2',
  toastSelector(profile) {
    return profile.ui.toast_selector;
  },
  inputSelector(label, _profile) {
    return `input[placeholder="${label}"]`;
  },
  assertionSnippet(ac, profile) {
    if (ac.then.observable === 'toast' && ac.then.expect_text) {
      return `await expect(page.locator('${profile.ui.toast_selector}'))`
        + `.toContainText('${ac.then.expect_text}');`;
    }
    if (ac.then.observable === 'url' && ac.then.expect_value) {
      return `await expect(page).toHaveURL(/${ac.then.expect_value}/);`;
    }
    return `await expect(page.locator('body')).toContainText('${ac.then.expect_text ?? ''}');`;
  },
};
