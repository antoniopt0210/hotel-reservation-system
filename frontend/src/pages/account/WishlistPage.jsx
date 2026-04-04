import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchWishlist } from '../../api/wishlist';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import StarRating from '../../components/common/StarRating';
import WishlistButton from '../../components/common/WishlistButton';

const WishlistPage = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['wishlist'],
    queryFn: fetchWishlist,
  });

  if (isLoading) return <LoadingSpinner className="py-32" size="lg" />;

  const items = data?.wishlist || [];

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Wishlist</h1>

      {items.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          <p className="text-5xl mb-4">{'\u2661'}</p>
          <p>Your wishlist is empty. Browse hotels and tap the heart to save them.</p>
        </div>
      )}

      <div className="space-y-4">
        {items.map(({ hotel_id, hotel }) => {
          if (!hotel) return null;
          const photo = hotel.photos?.find(p => p.is_primary) || hotel.photos?.[0];
          return (
            <Link
              key={hotel_id}
              to={`/hotels/${hotel.slug}`}
              className="block bg-white rounded-xl shadow hover:shadow-md transition overflow-hidden"
            >
              <div className="flex flex-col sm:flex-row">
                <img
                  src={photo?.url || 'https://picsum.photos/seed/default/400/260'}
                  alt={hotel.name}
                  className="sm:w-48 h-36 object-cover shrink-0"
                />
                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <h2 className="font-bold text-gray-800 text-lg">{hotel.name}</h2>
                      <div className="flex items-center gap-2">
                        <WishlistButton hotelId={hotel_id} />
                        <StarRating rating={hotel.star_rating} size="sm" />
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{hotel.city}, {hotel.country}</p>
                  </div>
                  {hotel.min_price && (
                    <p className="mt-2 text-blue-600 font-bold">From ${hotel.min_price}/night</p>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default WishlistPage;
