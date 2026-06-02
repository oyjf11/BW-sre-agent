import { describe, it, expect, vi, beforeEach } from 'vitest';
import { runs } from './runs';
import * as apiModule from './api';

vi.mock('./api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApi = apiModule.api as ReturnType<typeof vi.fn>;

describe('runs', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('createRun', () => {
    it('creates a new run with ticket data', async () => {
      const mockRun = {
        run_id: 'run-123',
        thread_id: 'thread-456',
        status: 'running',
        created_at: '2024-01-15T10:00:00Z',
      };
      
      vi.mocked(mockApi.post).mockResolvedValue(mockRun);

      const ticket = {
        ticket_id: 'INC-001',
        title: 'Test incident',
        description: 'Test description',
        service: 'api-gateway',
        env: 'prod',
        severity: 'P1',
        source: 'manual',
      };

      const result = await runs.createRun({ ticket });
      
      expect(mockApi.post).toHaveBeenCalledWith('/incidents/runs', { ticket });
      expect(result).toEqual(mockRun);
    });
  });

  describe('getRun', () => {
    it('fetches run by ID', async () => {
      const mockRunDetail = {
        run_id: 'run-123',
        thread_id: 'thread-456',
        status: 'running',
        created_at: '2024-01-15T10:00:00Z',
      };
      
      vi.mocked(mockApi.get).mockResolvedValue(mockRunDetail);

      const result = await runs.getRun('run-123');
      
      expect(mockApi.get).toHaveBeenCalledWith('/incidents/runs/run-123');
      expect(result).toEqual(mockRunDetail);
    });
  });

  describe('listRuns', () => {
    it('fetches runs with default pagination', async () => {
      const mockRuns = [
        { run_id: 'run-1', status: 'completed', created_at: '2024-01-15T10:00:00Z' },
        { run_id: 'run-2', status: 'running', created_at: '2024-01-15T11:00:00Z' },
      ];
      
      vi.mocked(mockApi.get).mockResolvedValue(mockRuns);

      const result = await runs.listRuns();
      
      expect(mockApi.get).toHaveBeenCalledWith('/incidents/runs?limit=100&offset=0');
      expect(result).toEqual(mockRuns);
    });

    it('fetches runs with custom pagination', async () => {
      const mockRuns = [{ run_id: 'run-1', status: 'completed', created_at: '2024-01-15T10:00:00Z' }];
      
      vi.mocked(mockApi.get).mockResolvedValue(mockRuns);

      await runs.listRuns(10, 20);
      
      expect(mockApi.get).toHaveBeenCalledWith('/incidents/runs?limit=10&offset=20');
    });
  });

  describe('getRunEvents', () => {
    it('fetches events without event ID', async () => {
      const mockEvents = [
        { event_id: 'ev-1', run_id: 'run-123', level: 'INFO', message: 'Started', timestamp: '2024-01-15T10:00:00Z' },
      ];
      
      vi.mocked(mockApi.get).mockResolvedValue(mockEvents);

      const result = await runs.getRunEvents('run-123');
      
      expect(mockApi.get).toHaveBeenCalledWith('/incidents/runs/run-123/events');
      expect(result).toEqual(mockEvents);
    });

    it('fetches events after the last event ID', async () => {
      const mockEvents = [
        {
          event_id: 'evt-2',
          run_id: 'run-123',
          level: 'INFO',
          message: 'Updated',
          timestamp: '2026-06-02T10:00:01Z',
        },
      ];
      
      vi.mocked(mockApi.get).mockResolvedValue(mockEvents);

      const result = await runs.getRunEvents('run-123', 'evt-1');
      
      expect(mockApi.get).toHaveBeenCalledWith(
        '/incidents/runs/run-123/events?last_event_id=evt-1',
      );
      expect(result).toEqual(mockEvents);
    });
  });

  describe('getRunRca', () => {
    it('fetches RCA report for a run', async () => {
      const mockRca = {
        run_id: 'run-123',
        report_markdown: '# Root Cause Analysis',
        root_cause: 'Database connection pool exhausted',
        resolution: 'Increased pool size',
        prevention_items: ['Add monitoring', 'Set alerts'],
        confirmed_by_human: false,
      };
      
      vi.mocked(mockApi.get).mockResolvedValue(mockRca);

      const result = await runs.getRunRca('run-123');
      
      expect(mockApi.get).toHaveBeenCalledWith('/incidents/runs/run-123/rca');
      expect(result).toEqual(mockRca);
    });
  });
});
