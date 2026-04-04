import client from './client';

export const fetchReservations = () =>
  client.get('/api/reservations').then((r) => r.data.reservations);

export const createReservation = (data) =>
  client.post('/api/reservations', data).then((r) => r.data);

export const updateReservationStatus = (id, status, checkInDate) =>
  client
    .put(`/api/reservations/${id}`, { status, check_in_date: checkInDate })
    .then((r) => r.data);

export const deleteReservation = (id, checkInDate) => {
  const params = checkInDate ? { check_in_date: checkInDate } : {};
  return client.delete(`/api/reservations/${id}`, { params }).then((r) => r.data);
};
