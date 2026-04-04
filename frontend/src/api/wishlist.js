import api from './client';

export const fetchWishlist = () =>
  api.get('/v1/wishlist').then(r => r.data);

export const addToWishlist = (hotelId) =>
  api.post(`/v1/wishlist/${hotelId}`).then(r => r.data);

export const removeFromWishlist = (hotelId) =>
  api.delete(`/v1/wishlist/${hotelId}`).then(r => r.data);
