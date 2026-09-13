import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export const useApiQuery = (key: string[], url: string) => {
  return useQuery({
    queryKey: key,
    queryFn: () => apiClient(url)
  });
};