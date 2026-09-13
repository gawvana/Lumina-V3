export const apiClient = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const headers = new Headers(options.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  headers.set('Content-Type', 'application/json');
  
  const response = await fetch(`/api${url}`, { ...options, headers });
  if (!response.ok) {
    throw new Error('API Error');
  }
  return response.json();
};