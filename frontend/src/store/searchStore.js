import { create } from 'zustand';

const useSearchStore = create((set) => ({
  city: '',
  checkIn: '',
  checkOut: '',
  guests: 1,
  filters: {
    minPrice: 0,
    maxPrice: 1000,
    stars: [],
    amenities: [],
  },

  setSearchParams: (params) => set((state) => ({ ...state, ...params })),
  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters } })),
  reset: () =>
    set({
      city: '',
      checkIn: '',
      checkOut: '',
      guests: 1,
      filters: { minPrice: 0, maxPrice: 1000, stars: [], amenities: [] },
    }),
}));

export default useSearchStore;
