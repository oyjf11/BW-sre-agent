import { SelectorAdapter, notImplemented } from './types';

export const react16MinusAdapter: SelectorAdapter = {
  framework: 'react16-minus',
  toastSelector: () => notImplemented('react16-minus'),
  inputSelector: () => notImplemented('react16-minus'),
  assertionSnippet: () => notImplemented('react16-minus'),
};
