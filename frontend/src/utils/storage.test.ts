import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getItem, setItem, removeItem, clear } from './storage';

const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((i: number) => Object.keys(store)[i] || null),
    getStore: () => store,
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
});

describe('storage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
  });

  describe('getItem', () => {
    it('returns parsed JSON value from localStorage', () => {
      localStorageMock.setItem('opspilot_test', JSON.stringify({ key: 'value' }));
      
      const result = getItem('test', { default: 'fallback' });
      expect(result).toEqual({ key: 'value' });
    });

    it('returns fallback when key not found', () => {
      const fallback = { default: 'fallback' };
      const result = getItem('nonexistent', fallback);
      expect(result).toEqual(fallback);
    });

    it('returns fallback when localStorage throws', () => {
      vi.spyOn(localStorageMock, 'getItem').mockImplementation(() => {
        throw new Error('Storage error');
      });
      
      const result = getItem('test', 'fallback');
      expect(result).toBe('fallback');
    });
  });

  describe('setItem', () => {
    it('stores JSON stringified value', () => {
      setItem('test', { key: 'value' });
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'opspilot_test',
        JSON.stringify({ key: 'value' })
      );
    });

    it('handles primitive values', () => {
      setItem('string', 'value');
      setItem('number', 123);
      setItem('boolean', true);
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('opspilot_string', '"value"');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('opspilot_number', '123');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('opspilot_boolean', 'true');
    });
  });

  describe('removeItem', () => {
    it('removes item from localStorage', () => {
      localStorageMock.setItem('opspilot_test', 'value');
      
      removeItem('test');
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('opspilot_test');
    });
  });

  describe('clear', () => {
    it('removes all opspilot prefixed items', () => {
      localStorageMock.setItem('opspilot_test1', 'value1');
      localStorageMock.setItem('opspilot_test2', 'value2');
      localStorageMock.setItem('other_key', 'value3');
      Object.keys(localStorageMock.getStore()).forEach((key, index) => {
        vi.mocked(localStorageMock.key).mockImplementationOnce((i: number) => (i === index ? key : null));
      });
      
      clear();
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('opspilot_test1');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('opspilot_test2');
      expect(localStorageMock.removeItem).not.toHaveBeenCalledWith('other_key');
    });
  });
});
