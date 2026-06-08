import * as fs from 'fs';
import * as path from 'path';
import { Framework } from './contracts';

interface PkgJson {
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
}

function cleanVer(v: string): string {
  return v.replace(/^[\^~>=<\s]+/, '');
}
function majorMinor(v: string): { major: number; minor: number } {
  const parts = cleanVer(v).split('.');
  const major = parseInt(parts[0], 10);
  const minorStr = parts[1] || '0';
  // 'x' wildcard or non-numeric minor → treat as 0 (conservative; caller decides)
  const minor = isNaN(parseInt(minorStr, 10)) ? 0 : parseInt(minorStr, 10);
  return { major, minor };
}

export function detectFramework(pkg: PkgJson): Framework {
  const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
  if (deps.vue) {
    const { major } = majorMinor(deps.vue);
    if (major === 2) return 'vue2';
    if (major >= 3) return 'vue3';
  }
  if (deps.react) {
    const { major, minor } = majorMinor(deps.react);
    if (major > 16 || (major === 16 && minor >= 8)) return 'react16-plus';
    return 'react16-minus';
  }
  throw new Error('unsupported framework: no vue/react dependency found');
}

export function detectFromProject(root: string): Framework {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf-8'));
  return detectFramework(pkg);
}
