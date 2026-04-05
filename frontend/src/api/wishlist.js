import api from './client';

export const fetchWishlist = () =>
  api.get('/api/v1/wishlist').then(r => r.data);

export const addToWishlist = (hotelId) =>
  api.post(`/api/v1/wishlist/${hotelId}`).then(r => r.data);

export const removeFromWishlist = (hotelId) =>
  api.delete(`/api/v1/wishlist/${hotelId}`).then(r => r.data);
