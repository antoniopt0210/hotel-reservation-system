import api from './client';

export const fetchAutocomplete = (q) =>
  api.get('/api/v1/search/autocomplete', { params: { q } }).then(r => r.data);
