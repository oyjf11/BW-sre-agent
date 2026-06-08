import { Framework } from '../contracts';
import { SelectorAdapter } from './types';
import { vue2Adapter } from './vue2';
import { vue3Adapter } from './vue3';
import { react16MinusAdapter } from './react16-minus';
import { react16PlusAdapter } from './react16-plus';

const REGISTRY: Record<Framework, SelectorAdapter> = {
  vue2: vue2Adapter,
  vue3: vue3Adapter,
  'react16-minus': react16MinusAdapter,
  'react16-plus': react16PlusAdapter,
};

export function getAdapter(framework: Framework): SelectorAdapter {
  return REGISTRY[framework];
}

export type { SelectorAdapter } from './types';
