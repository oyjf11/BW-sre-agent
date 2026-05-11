import { describe, it, expect, beforeEach, vi } from 'vitest';
import { parseUrlQuery, setUrlQuery, getQueryParam } from './query';

const mockHistory = {
  replaceState: vi.fn(),
};

Object.defineProperty(global, 'history', {
  value: mockHistory,
});

describe('query', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete (global as any).window.location;
    (global as any).window.location = new URL('http://localhost?foo=bar&baz=qux');
  });

  describe('parseUrlQuery', () => {
    it('parses query parameters into object', () => {
      const result = parseUrlQuery<{ foo: string; baz: string }>();
      
      expect(result).toEqual({ foo: 'bar', baz: 'qux' });
    });

    it('returns empty object when no query params', () => {
      (global as any).window.location = new URL('http://localhost');
      
      const result = parseUrlQuery<Record<string, string>>();
      
      expect(result).toEqual({});
    });
  });

  describe('setUrlQuery', () => {
    it('sets query parameter', () => {
      setUrlQuery({ newParam: 'newValue' });
      
      expect(mockHistory.replaceState).toHaveBeenCalled();
    });

    it('removes query parameter when value is empty', () => {
      setUrlQuery({ foo: '' });
      
      expect(mockHistory.replaceState).toHaveBeenCalled();
    });
  });

  describe('getQueryParam', () => {
    it('returns query param value', () => {
      const result = getQueryParam('foo');
      expect(result).toBe('bar');
    });

    it('returns null when param not found', () => {
      const result = getQueryParam('nonexistent');
      expect(result).toBeNull();
    });
  });
});
