export function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function isZhCN(): boolean {
  try {
    return localStorage.getItem('opspilot-locale') === 'zh-CN';
  } catch {
    return false;
  }
}

export function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diff = now.getTime() - then.getTime();
  const zh = isZhCN();

  if (diff < 60000) return zh ? '刚刚' : 'just now';
  if (diff < 3600000) return zh ? `${Math.floor(diff / 60000)} 分钟前` : `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return zh ? `${Math.floor(diff / 3600000)} 小时前` : `${Math.floor(diff / 3600000)}h ago`;
  return formatTime(timestamp);
}
