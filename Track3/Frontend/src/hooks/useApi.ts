import { useState, useCallback } from 'react';

interface ApiResponse<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T = any> extends ApiResponse<T> {
  execute: (url: string, options?: RequestInit) => Promise<T | null>;
}

const API_BASE_URL = 'https://blood-management-system-xplx.onrender.com';

export const useApi = <T = any>(): UseApiReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (url: string, options: RequestInit = {}): Promise<T | null> => {
    try {
      setLoading(true);
      setError(null);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('authToken');
      
      // Prepare headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> || {}),
      };
      
      // Add authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Make the API call
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      setData(result);
      return result;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
      console.error('API Error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    data,
    loading,
    error,
    execute,
  };
};

export default useApi;
