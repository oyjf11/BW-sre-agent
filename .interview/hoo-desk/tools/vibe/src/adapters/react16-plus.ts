import { SelectorAdapter, notImplemented } from './types';

export const react16PlusAdapter: SelectorAdapter = {
  framework: 'react16-plus',
  toastSelector: () => notImplemented('react16-plus'),
  inputSelector: () => notImplemented('react16-plus'),
  assertionSnippet: () => notImplemented('react16-plus'),
};
