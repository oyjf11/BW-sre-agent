import { SelectorAdapter, notImplemented } from './types';

export const vue3Adapter: SelectorAdapter = {
  framework: 'vue3',
  toastSelector: () => notImplemented('vue3'),
  inputSelector: () => notImplemented('vue3'),
  assertionSnippet: () => notImplemented('vue3'),
};
