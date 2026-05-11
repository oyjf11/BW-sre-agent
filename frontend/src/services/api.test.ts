import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, ApiError } from './api';

describe('api', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('get', () => {
    it('makes GET request successfully', async () => {
      const mockData = { id: '1', name: 'test' };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await api.get('/test');
      expect(result).toEqual(mockData);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('throws ApiError on failed response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not found' }),
      });

      await expect(api.get('/not-found')).rejects.toThrow(ApiError);
    });

    it('throws ApiError with correct status on 404', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not found' }),
      });

      await expect(api.get('/not-found')).rejects.toMatchObject({
        status: 404,
        message: 'Not found',
      });
    });
  });

  describe('post', () => {
    it('makes POST request with JSON body', async () => {
      const mockData = { id: '1', name: 'test' };
      const postData = { name: 'test' };
      
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await api.post('/test', postData);
      expect(result).toEqual(mockData);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      );
    });
  });

  describe('put', () => {
    it('makes PUT request with JSON body', async () => {
      const mockData = { id: '1', name: 'updated' };
      const putData = { name: 'updated' };
      
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await api.put('/test/1', putData);
      expect(result).toEqual(mockData);
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test/1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData),
        })
      );
    });
  });

  describe('delete', () => {
    it('makes DELETE request', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });

      await api.delete('/test/1');
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  describe('ApiError', () => {
    it('creates error with correct status and message', () => {
      const error = new ApiError(500, 'Internal server error');
      expect(error.name).toBe('ApiError');
      expect(error.status).toBe(500);
      expect(error.message).toBe('Internal server error');
    });
  });
});
