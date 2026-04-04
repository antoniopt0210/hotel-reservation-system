/**
 * Hotels API — implemented in Phase 2.
 */
import client from './client';

export const fetchHotels = (params) =>
  client.get('/api/v1/hotels', { params }).then((r) => r.data);

export const fetchHotel = (slug) =>
  client.get(`/api/v1/hotels/${slug}`).then((r) => r.data);

export const fetchHotelRooms = (hotelId, params) =>
  client.get(`/api/v1/hotels/${hotelId}/rooms`, { params }).then((r) => r.data);

export const fetchAmenities = () =>
  client.get('/api/v1/hotels/amenities').then((r) => r.data);
