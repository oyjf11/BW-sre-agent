export function parseUrlQuery<T extends Record<string, string>>(): T {
  const params = new URLSearchParams(window.location.search);
  const result: Record<string, string> = {};
  params.forEach((value, key) => {
    result[key] = value;
  });
  return result as T;
}

export function setUrlQuery(params: Record<string, string>): void {
  const url = new URL(window.location.href);
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      url.searchParams.set(key, value);
    } else {
      url.searchParams.delete(key);
    }
  });
  window.history.replaceState({}, '', url.toString());
}

export function getQueryParam(key: string): string | null {
  return new URLSearchParams(window.location.search).get(key);
}
