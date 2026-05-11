import { describe, it, expect } from 'vitest';
import { formatJson, truncate, pluralize } from './format';

describe('format', () => {
  describe('formatJson', () => {
    it('formats object as JSON string', () => {
      const data = { name: 'test', value: 123 };
      const result = formatJson(data);
      expect(result).toBe('{\n  "name": "test",\n  "value": 123\n}');
    });

    it('formats array as JSON string', () => {
      const data = [1, 2, 3];
      const result = formatJson(data);
      expect(result).toBe('[\n  1,\n  2,\n  3\n]');
    });

    it('formats null', () => {
      expect(formatJson(null)).toBe('null');
    });
  });

  describe('truncate', () => {
    it('returns original string if shorter than max length', () => {
      expect(truncate('hello', 10)).toBe('hello');
    });

    it('truncates string longer than max length', () => {
      expect(truncate('hello world', 8)).toBe('hello...');
    });

    it('handles exact max length', () => {
      expect(truncate('hello', 5)).toBe('hello');
    });

    it('handles empty string', () => {
      expect(truncate('', 5)).toBe('');
    });
  });

  describe('pluralize', () => {
    it('returns singular for count of 1', () => {
      expect(pluralize(1, 'item')).toBe('item');
    });

    it('returns plural for count other than 1', () => {
      expect(pluralize(0, 'item')).toBe('items');
      expect(pluralize(2, 'item')).toBe('items');
      expect(pluralize(100, 'item')).toBe('items');
    });

    it('uses custom plural form', () => {
      expect(pluralize(1, 'entry', 'entries')).toBe('entry');
      expect(pluralize(2, 'entry', 'entries')).toBe('entries');
    });

    it('handles count of 1 with default plural', () => {
      expect(pluralize(1, 'status')).toBe('status');
      expect(pluralize(2, 'status')).toBe('statuss');
    });
  });
});
