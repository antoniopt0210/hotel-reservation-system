import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { fetchWishlist, addToWishlist, removeFromWishlist } from '../../api/wishlist';
import useAuthStore from '../../store/authStore';

const WishlistButton = ({ hotelId, className = '' }) => {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState(false);

  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: fetchWishlist,
    enabled: !!user,
  });

  useEffect(() => {
    if (wishlistData?.wishlist) {
      setSaved(wishlistData.wishlist.some(w => w.hotel_id === hotelId));
    }
  }, [wishlistData, hotelId]);

  const { mutate: toggle } = useMutation({
    mutationFn: () => saved ? removeFromWishlist(hotelId) : addToWishlist(hotelId),
    onSuccess: () => {
      setSaved(!saved);
      queryClient.invalidateQueries(['wishlist']);
    },
  });

  if (!user) return null;

  return (
    <button
      onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggle(); }}
      className={`text-2xl transition hover:scale-110 ${className}`}
      title={saved ? 'Remove from wishlist' : 'Save to wishlist'}
    >
      <span className={saved ? 'text-red-500' : 'text-gray-300 hover:text-red-300'}>
        {saved ? '\u2665' : '\u2661'}
      </span>
    </button>
  );
};

export default WishlistButton;
