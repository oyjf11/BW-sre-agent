import { describe, it, expect, vi, beforeEach } from 'vitest';
import { formatTime, formatDuration, formatRelativeTime } from './time';

describe('time', () => {
  describe('formatTime', () => {
    it('formats ISO timestamp', () => {
      const result = formatTime('2024-01-15T10:30:00Z');
      expect(result).toContain('2024');
      expect(result).toMatch(/30:00/);
    });
  });

  describe('formatDuration', () => {
    it('formats milliseconds less than 1 second', () => {
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(0)).toBe('0ms');
      expect(formatDuration(999)).toBe('999ms');
    });

    it('formats seconds', () => {
      expect(formatDuration(1000)).toBe('1.0s');
      expect(formatDuration(5500)).toBe('5.5s');
      expect(formatDuration(59999)).toBe('60.0s');
    });

    it('formats minutes', () => {
      expect(formatDuration(60000)).toBe('1.0m');
      expect(formatDuration(90000)).toBe('1.5m');
      expect(formatDuration(3600000)).toBe('60.0m');
    });
  });

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it('returns "just now" for timestamps less than 1 minute ago', () => {
      const now = new Date('2024-01-15T12:00:00Z');
      vi.setSystemTime(now);
      
      const result = formatRelativeTime('2024-01-15T12:00:00Z');
      expect(result).toBe('just now');
    });

    it('returns minutes ago for timestamps less than 1 hour ago', () => {
      const now = new Date('2024-01-15T12:00:00Z');
      vi.setSystemTime(now);
      
      const result = formatRelativeTime('2024-01-15T11:59:00Z');
      expect(result).toBe('1m ago');
    });

    it('returns hours ago for timestamps less than 1 day ago', () => {
      const now = new Date('2024-01-15T12:00:00Z');
      vi.setSystemTime(now);
      
      const result = formatRelativeTime('2024-01-15T10:00:00Z');
      expect(result).toBe('2h ago');
    });

    it('returns formatted time for timestamps older than 1 day', () => {
      const now = new Date('2024-01-15T12:00:00Z');
      vi.setSystemTime(now);
      
      const result = formatRelativeTime('2024-01-10T12:00:00Z');
      expect(result).not.toContain('ago');
    });
  });
});
