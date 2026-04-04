import { useState, useCallback } from 'react';

const STORAGE_KEY = 'recently_viewed_hotels';
const MAX_ITEMS = 6;

const getStored = () => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
};

export const addRecentlyViewed = (hotel) => {
  const items = getStored().filter(h => h.id !== hotel.id);
  items.unshift({
    id:          hotel.id,
    name:        hotel.name,
    slug:        hotel.slug,
    city:        hotel.city,
    country:     hotel.country,
    star_rating: hotel.star_rating,
    min_price:   hotel.min_price,
    photo:       hotel.photos?.[0]?.url || null,
    avg_rating:  hotel.avg_rating,
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, MAX_ITEMS)));
};

export const useRecentlyViewed = () => {
  const [items] = useState(getStored);
  const add = useCallback(addRecentlyViewed, []);
  return { items, add };
};
