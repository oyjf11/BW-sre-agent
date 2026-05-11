import { describe, it, expect, vi, beforeEach } from 'vitest';
import { exportJson, exportEventsJson, exportEvidenceJson } from './export';

describe('export', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock document.createElement
    const mockA = {
      href: '',
      download: '',
      click: vi.fn(),
    };
    
    vi.spyOn(document, 'createElement').mockReturnValue(mockA as any);
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:http://localhost');
    vi.spyOn(URL, 'revokeObjectURL').mockReturnValue();
    vi.spyOn(document.body, 'appendChild');
    vi.spyOn(document.body, 'removeChild');
  });

  describe('exportJson', () => {
    it('creates blob and triggers download', () => {
      const data = { name: 'test' };
      
      exportJson(data, 'test.json');
      
      expect(URL.createObjectURL).toHaveBeenCalled();
      expect(document.createElement).toHaveBeenCalledWith('a');
    });

    it('revokes object URL after download', () => {
      const data = { name: 'test' };
      
      exportJson(data, 'test.json');
      
      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:http://localhost');
    });

    it('uses correct filename', () => {
      const data = { name: 'test' };
      
      exportJson(data, 'custom-file.json');
      
      const mockA = (document.createElement as ReturnType<typeof vi.fn>).mock.results[0].value;
      expect(mockA.download).toBe('custom-file.json');
    });
  });

  describe('exportEventsJson', () => {
    it('exports events with timestamp filename', () => {
      const events = [{ id: 1 }, { id: 2 }];
      const before = Date.now();
      
      exportEventsJson(events);
      
      const after = Date.now();
      const mockA = (document.createElement as ReturnType<typeof vi.fn>).mock.results[0].value;
      const filename = mockA.download;
      
      expect(filename).toMatch(/^events-\d+\.json$/);
      const timestamp = parseInt(filename.replace('events-', '').replace('.json', ''));
      expect(timestamp).toBeGreaterThanOrEqual(before);
      expect(timestamp).toBeLessThanOrEqual(after);
    });
  });

  describe('exportEvidenceJson', () => {
    it('exports evidence with timestamp filename', () => {
      const evidence = [{ id: 1 }];
      
      exportEvidenceJson(evidence);
      
      const mockA = (document.createElement as ReturnType<typeof vi.fn>).mock.results[0].value;
      const filename = mockA.download;
      
      expect(filename).toMatch(/^evidence-\d+\.json$/);
    });
  });
});
