import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { fetchHotel, fetchHotelRooms } from '../api/hotels';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StarRating from '../components/common/StarRating';
import Button from '../components/common/Button';
import ReviewList from '../components/reviews/ReviewList';
import ReviewForm from '../components/reviews/ReviewForm';
import WishlistButton from '../components/common/WishlistButton';
import LocationMap from '../components/hotel/LocationMap';
import useAuthStore from '../store/authStore';

const HotelDetailPage = () => {
  const { slug }            = useParams();
  const [searchParams]      = useSearchParams();
  const navigate            = useNavigate();

  const checkIn  = searchParams.get('check_in')  || '';
  const checkOut = searchParams.get('check_out') || '';
  const guests   = searchParams.get('guests')    || 1;

  const { user }                    = useAuthStore();
  const [hotel, setHotel]           = useState(null);
  const [rooms, setRooms]           = useState([]);
  const [heroIndex, setHeroIndex]   = useState(0);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [showReviewForm, setShowReviewForm] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchHotel(slug),
      fetchHotelRooms(slug, { check_in: checkIn, check_out: checkOut, guests }),
    ])
      .then(([hotelData, roomData]) => {
        setHotel(hotelData.hotel);
        setRooms(roomData.rooms);
      })
      .catch(() => setError('Failed to load hotel details.'))
      .finally(() => setLoading(false));
  }, [slug, checkIn, checkOut, guests]);

  if (loading) return <LoadingSpinner className="py-32" size="lg" />;
  if (error)   return <p className="text-center text-red-500 py-20">{error}</p>;
  if (!hotel)  return null;

  const nights = checkIn && checkOut
    ? Math.max((new Date(checkOut) - new Date(checkIn)) / 86400000, 1)
    : 1;

  const photos = hotel.photos.length
    ? hotel.photos
    : [{ url: 'https://picsum.photos/seed/default/800/500', caption: hotel.name }];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Photo gallery */}
      <div className="rounded-xl overflow-hidden mb-6">
        <div className="relative">
          <img src={photos[heroIndex]?.url} alt={photos[heroIndex]?.caption || hotel.name}
            className="w-full h-80 object-cover" />
          {photos.length > 1 && (
            <>
              <button onClick={() => setHeroIndex(i => (i - 1 + photos.length) % photos.length)}
                className="absolute left-3 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-9 h-9 flex items-center justify-center hover:bg-black/70">
                ‹
              </button>
              <button onClick={() => setHeroIndex(i => (i + 1) % photos.length)}
                className="absolute right-3 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full w-9 h-9 flex items-center justify-center hover:bg-black/70">
                ›
              </button>
            </>
          )}
        </div>
        {photos.length > 1 && (
          <div className="flex gap-2 mt-2 overflow-x-auto pb-1">
            {photos.map((p, i) => (
              <img key={i} src={p.url} alt="" onClick={() => setHeroIndex(i)}
                className={`h-16 w-24 object-cover rounded cursor-pointer shrink-0 border-2 transition ${i === heroIndex ? 'border-blue-500' : 'border-transparent'}`} />
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: hotel info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title */}
          <div>
            <div className="flex items-start justify-between gap-2 flex-wrap">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold text-gray-800">{hotel.name}</h1>
                <WishlistButton hotelId={hotel.id} />
              </div>
              <StarRating rating={hotel.star_rating} size="lg" />
            </div>
            {hotel.avg_rating && (
              <div className="flex items-center gap-1 mt-1">
                <span className="bg-blue-600 text-white text-sm font-bold px-2 py-0.5 rounded">
                  {hotel.avg_rating.toFixed(1)}
                </span>
                <span className="text-sm text-gray-500">
                  {hotel.review_count} review{hotel.review_count !== 1 ? 's' : ''}
                </span>
              </div>
            )}
            <p className="text-gray-500 mt-1">
              {[hotel.address_line1, hotel.city, hotel.state_province, hotel.country].filter(Boolean).join(', ')}
            </p>
          </div>

          {/* Description */}
          <p className="text-gray-700 leading-relaxed">{hotel.description}</p>

          {/* Amenities */}
          {hotel.amenities.length > 0 && (
            <div>
              <h2 className="font-bold text-gray-700 mb-3">Amenities</h2>
              <div className="flex flex-wrap gap-2">
                {hotel.amenities.map(a => (
                  <span key={a.id} className="flex items-center gap-1 bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
                    {a.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Reviews — Phase 4 */}
          <div className="border-t pt-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-gray-700 text-xl">Guest Reviews</h2>
              {user && !showReviewForm && (
                <Button variant="secondary" onClick={() => setShowReviewForm(true)}>
                  Write a review
                </Button>
              )}
            </div>
            {showReviewForm && (
              <ReviewForm
                hotelId={hotel.id}
                onSuccess={() => setShowReviewForm(false)}
              />
            )}
            <ReviewList hotelId={hotel.id} />
          </div>
        </div>

        {/* Right: booking info + map */}
        <div className="space-y-4">
          <div className="bg-white border rounded-xl shadow p-4 sticky top-4">
            <p className="text-sm text-gray-500 mb-1">Check-in / Check-out</p>
            <p className="font-semibold text-gray-800">
              {checkIn || '—'} → {checkOut || '—'}
            </p>
            <p className="text-sm text-gray-500 mt-2">{guests} guest{guests > 1 ? 's' : ''} · {nights} night{nights !== 1 ? 's' : ''}</p>
            <p className="text-xs text-gray-400 mt-1">
              Check-in: {hotel.check_in_time} · Check-out: {hotel.check_out_time}
            </p>
          </div>
          <LocationMap latitude={hotel.latitude} longitude={hotel.longitude} name={hotel.name} />
        </div>
      </div>

      {/* Available rooms */}
      <div className="mt-10">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Available Rooms</h2>
        {rooms.length === 0 && (
          <p className="text-gray-500">No rooms available for the selected dates.</p>
        )}
        <div className="space-y-4">
          {rooms.map(room => {
            const photo = room.photos[0];
            const totalPrice = (room.base_price_usd * nights).toFixed(0);
            return (
              <div key={room.id} className="bg-white border rounded-xl overflow-hidden flex flex-col sm:flex-row shadow-sm hover:shadow transition">
                <img
                  src={photo?.url || 'https://picsum.photos/seed/room/400/260'}
                  alt={room.name}
                  className="sm:w-48 h-36 object-cover shrink-0"
                />
                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between flex-wrap gap-1">
                      <h3 className="font-semibold text-gray-800">{room.name}</h3>
                      <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{room.room_type}</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{room.description}</p>
                    <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
                      <span>👤 Up to {room.max_occupancy} guests</span>
                      {room.size_sqft && <span>📐 {room.size_sqft} sq ft</span>}
                      {room.bed_count && <span>🛏 {room.bed_count} bed{room.bed_count > 1 ? 's' : ''}</span>}
                    </div>
                  </div>
                  <div className="mt-3 flex items-end justify-between">
                    <div>
                      <p className="text-xl font-bold text-blue-600">${totalPrice}</p>
                      <p className="text-xs text-gray-400">${room.base_price_usd}/night · {nights} night{nights !== 1 ? 's' : ''}</p>
                    </div>
                    <Button
                      onClick={() =>
                        navigate(`/booking/details?room_id=${room.id}&hotel_slug=${slug}&check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`)
                      }
                    >
                      Reserve
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default HotelDetailPage;
