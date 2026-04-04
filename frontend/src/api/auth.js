/**
 * Auth API — implemented in Phase 2.
 */
import client from './client';

export const register = (data) =>
  client.post('/api/v1/auth/register', data).then((r) => r.data);

export const login = (email, password) =>
  client.post('/api/v1/auth/login', { email, password }).then((r) => r.data);

export const logout = () =>
  client.post('/api/v1/auth/logout').then((r) => r.data);

export const getMe = () =>
  client.get('/api/v1/auth/me').then((r) => r.data);
