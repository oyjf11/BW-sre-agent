import { AcCriterion, Framework, Profile } from '../contracts';

export interface SelectorAdapter {
  framework: Framework;
  toastSelector(profile: Profile): string;
  inputSelector(label: string, profile: Profile): string;
  assertionSnippet(ac: AcCriterion, profile: Profile): string;
}

export function notImplemented(framework: Framework): never {
  throw new Error(`selector adapter for "${framework}" is not implemented yet`);
}
