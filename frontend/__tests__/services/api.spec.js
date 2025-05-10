import axios from 'axios';
import { apiService } from '../../src/services/api';

// axios 모킹
jest.mock('axios', () => {
  return {
    create: jest.fn(() => ({
      interceptors: {
        request: {
          use: jest.fn(),
        },
        response: {
          use: jest.fn(),
        },
      },
    })),
  };
});

describe('API Service', () => {
  it('creates axios instance with correct config', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }),
        withCredentials: true,
      })
    );
  });
  
  it('sets up request interceptors', () => {
    const mockAxiosInstance = axios.create();
    expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
  });
  
  it('sets up response interceptors', () => {
    const mockAxiosInstance = axios.create();
    expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
  });
}); 