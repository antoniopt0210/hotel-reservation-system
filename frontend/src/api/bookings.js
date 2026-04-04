import client from './client';

export const createPaymentIntent = (roomId, checkIn, checkOut) =>
  client.post('/api/v1/bookings/payment-intent', {
    room_id: roomId, check_in: checkIn, check_out: checkOut,
  }).then(r => r.data);

export const confirmBooking = (payload) =>
  client.post('/api/v1/bookings', payload).then(r => r.data);

export const fetchMyBookings = () =>
  client.get('/api/v1/bookings/mine').then(r => r.data);

export const fetchBooking = (id) =>
  client.get(`/api/v1/bookings/${id}`).then(r => r.data);

export const cancelBooking = (id, reason = '') =>
  client.put(`/api/v1/bookings/${id}/cancel`, { reason }).then(r => r.data);
