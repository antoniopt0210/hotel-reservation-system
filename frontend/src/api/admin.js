import api from './client';

export const fetchAdminStats = () =>
  api.get('/v1/admin/stats').then(r => r.data);

export const fetchAdminBookings = (params = {}) =>
  api.get('/v1/admin/bookings', { params }).then(r => r.data);

export const updateBookingStatus = (bookingId, status) =>
  api.put(`/v1/admin/bookings/${bookingId}/status`, { status }).then(r => r.data);

export const fetchAdminUsers = (params = {}) =>
  api.get('/v1/admin/users', { params }).then(r => r.data);

export const updateUserRole = (userId, role) =>
  api.put(`/v1/admin/users/${userId}/role`, { role }).then(r => r.data);
