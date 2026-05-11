import { describe, it, expect } from 'vitest';
import { safeJsonParse, safeStringify } from './safeJson';

describe('safeJson', () => {
  describe('safeJsonParse', () => {
    it('parses valid JSON string', () => {
      const result = safeJsonParse('{"key": "value"}', {});
      expect(result).toEqual({ key: 'value' });
    });

    it('parses valid JSON array', () => {
      const result = safeJsonParse('[1, 2, 3]', []);
      expect(result).toEqual([1, 2, 3]);
    });

    it('parses valid JSON primitive', () => {
      expect(safeJsonParse('"string"', '')).toBe('string');
      expect(safeJsonParse('123', 0)).toBe(123);
      expect(safeJsonParse('true', false)).toBe(true);
    });

    it('returns fallback for invalid JSON', () => {
      expect(safeJsonParse('invalid', 'fallback')).toBe('fallback');
      expect(safeJsonParse('{broken}', {})).toEqual({});
      expect(safeJsonParse('', 'empty')).toBe('empty');
    });

    it('returns fallback for empty string', () => {
      expect(safeJsonParse('', 'default')).toBe('default');
    });
  });

  describe('safeStringify', () => {
    it('stringifies object', () => {
      const result = safeStringify({ key: 'value' });
      expect(result).toBe('{"key":"value"}');
    });

    it('stringifies array', () => {
      const result = safeStringify([1, 2, 3]);
      expect(result).toBe('[1,2,3]');
    });

    it('stringifies primitives', () => {
      expect(safeStringify('string')).toBe('"string"');
      expect(safeStringify(123)).toBe('123');
      expect(safeStringify(true)).toBe('true');
    });

    it('returns fallback for circular reference', () => {
      const obj: any = { a: 1 };
      obj.self = obj;
      
      const result = safeStringify(obj, 'CIRCULAR');
      expect(result).toBe('CIRCULAR');
    });

    it('uses custom fallback', () => {
      const obj: any = { a: 1 };
      obj.self = obj;
      
      const result = safeStringify(obj, 'custom fallback');
      expect(result).toBe('custom fallback');
    });
  });
});
