import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,

  setAuth: (user, token) => {
    localStorage.setItem('access_token', token);
    set({ user, token });
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    set({ user: null, token: null });
  },
}));

export default useAuthStore;
