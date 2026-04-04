import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useSearchStore from '../store/searchStore';
import Button from '../components/common/Button';
import SearchAutocomplete from '../components/search/SearchAutocomplete';
import StarRating from '../components/common/StarRating';
import { useRecentlyViewed } from '../hooks/useRecentlyViewed';

const FEATURED_CITIES = [
  { city: 'New York',    img: 'https://picsum.photos/seed/nyc/400/260' },
  { city: 'Miami',       img: 'https://picsum.photos/seed/miami/400/260' },
  { city: 'Denver',      img: 'https://picsum.photos/seed/denver/400/260' },
  { city: 'Las Vegas',   img: 'https://picsum.photos/seed/vegas/400/260' },
  { city: 'Chicago',     img: 'https://picsum.photos/seed/chicago/400/260' },
  { city: 'Los Angeles', img: 'https://picsum.photos/seed/losangeles/400/260' },
];

const LandingPage = () => {
  const navigate = useNavigate();
  const { setSearchParams } = useSearchStore();
  const { items: recentlyViewed } = useRecentlyViewed();

  const today = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

  const [city, setCity]       = useState('');
  const [checkIn, setCheckIn] = useState(today);
  const [checkOut, setCheckOut] = useState(tomorrow);
  const [guests, setGuests]   = useState(1);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams({ city, checkIn, checkOut, guests });
    const params = new URLSearchParams({ city, check_in: checkIn, check_out: checkOut, guests });
    navigate(`/search?${params}`);
  };

  return (
    <div>
      {/* Hero */}
      <section
        className="relative bg-cover bg-center h-96 flex items-center justify-center"
        style={{ backgroundImage: "url('https://picsum.photos/seed/hotelhero/1400/600')" }}
      >
        <div className="absolute inset-0 bg-black/50" />
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">Find your perfect stay</h1>
          <p className="text-lg opacity-90">Hotels, resorts, and more — all in one place</p>
        </div>
      </section>

      {/* Search bar */}
      <section className="max-w-5xl mx-auto px-4 -mt-8 relative z-20">
        <form
          onSubmit={handleSearch}
          className="bg-white rounded-xl shadow-xl p-4 grid grid-cols-1 md:grid-cols-5 gap-3 items-end"
        >
          <div className="md:col-span-2 flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Destination</label>
            <SearchAutocomplete
              value={city}
              onChange={setCity}
              checkIn={checkIn}
              checkOut={checkOut}
              guests={guests}
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Check-in</label>
            <input type="date" value={checkIn} min={today}
              onChange={(e) => setCheckIn(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Check-out</label>
            <input type="date" value={checkOut} min={checkIn || today}
              onChange={(e) => setCheckOut(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Guests</label>
            <div className="flex gap-2">
              <input type="number" min={1} max={16} value={guests}
                onChange={(e) => setGuests(Number(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm w-20 focus:outline-none focus:ring-2 focus:ring-blue-400" />
              <Button type="submit" className="flex-1">Search</Button>
            </div>
          </div>
        </form>
      </section>

      {/* Featured destinations */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Popular destinations</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {FEATURED_CITIES.map(({ city: c, img }) => (
            <button
              key={c}
              onClick={() => {
                setSearchParams({ city: c, checkIn, checkOut, guests });
                navigate(`/search?city=${encodeURIComponent(c)}&check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`);
              }}
              className="relative rounded-xl overflow-hidden group cursor-pointer h-44"
            >
              <img src={img} alt={c} className="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
              <div className="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition duration-300" />
              <span className="absolute bottom-3 left-4 text-white font-semibold text-lg drop-shadow">{c}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Recently viewed */}
      {recentlyViewed.length > 0 && (
        <section className="max-w-6xl mx-auto px-4 pb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Recently viewed</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {recentlyViewed.slice(0, 4).map(h => (
              <Link
                key={h.id}
                to={`/hotels/${h.slug}`}
                className="bg-white rounded-xl shadow hover:shadow-md transition overflow-hidden"
              >
                <img
                  src={h.photo || 'https://picsum.photos/seed/default/400/260'}
                  alt={h.name}
                  className="w-full h-32 object-cover"
                />
                <div className="p-3">
                  <h3 className="font-semibold text-gray-800 text-sm truncate">{h.name}</h3>
                  <div className="flex items-center gap-1 mt-1">
                    <StarRating rating={h.star_rating} size="sm" />
                    {h.avg_rating && (
                      <span className="text-xs bg-blue-600 text-white px-1 rounded">{h.avg_rating.toFixed(1)}</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{h.city}, {h.country}</p>
                  {h.min_price && (
                    <p className="text-sm font-bold text-blue-600 mt-1">From ${h.min_price}/night</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Why StayEasy */}
      <section className="bg-blue-50 py-14">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          {[
            { icon: '🏨', title: 'Thousands of hotels', desc: 'From budget stays to 5-star luxury, every taste covered.' },
            { icon: '💳', title: 'No hidden fees',       desc: 'The price you see is the price you pay. Always.' },
            { icon: '🔒', title: 'Secure booking',       desc: 'Your payment and personal data are always protected.' },
          ].map(({ icon, title, desc }) => (
            <div key={title} className="flex flex-col items-center gap-2">
              <span className="text-4xl">{icon}</span>
              <h3 className="font-bold text-gray-800">{title}</h3>
              <p className="text-sm text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
