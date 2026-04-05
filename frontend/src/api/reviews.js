import api from './client';

export const fetchReviews = (hotelId, page = 1) =>
  api.get(`/api/v1/hotels/${hotelId}/reviews`, { params: { page, per_page: 5 } }).then(r => r.data);

export const fetchReviewSummary = (hotelId) =>
  api.get(`/api/v1/hotels/${hotelId}/reviews/summary`).then(r => r.data);

export const createReview = (hotelId, payload) =>
  api.post(`/api/v1/hotels/${hotelId}/reviews`, payload).then(r => r.data);

export const deleteReview = (reviewId) =>
  api.delete(`/api/v1/reviews/${reviewId}`).then(r => r.data);
