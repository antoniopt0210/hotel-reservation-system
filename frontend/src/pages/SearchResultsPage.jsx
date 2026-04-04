import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { fetchHotels, fetchAmenities } from '../api/hotels';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StarRating from '../components/common/StarRating';
import WishlistButton from '../components/common/WishlistButton';
import MobileFilterDrawer from '../components/search/MobileFilterDrawer';

const SearchResultsPage = () => {
  const [searchParams] = useSearchParams();
  const city     = searchParams.get('city') || '';
  const checkIn  = searchParams.get('check_in') || '';
  const checkOut = searchParams.get('check_out') || '';
  const guests   = searchParams.get('guests') || 1;

  const [hotels, setHotels]       = useState([]);
  const [amenities, setAmenities] = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [pages, setPages]         = useState(1);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  // Filters
  const [minPrice, setMinPrice]       = useState('');
  const [maxPrice, setMaxPrice]       = useState('');
  const [selectedStars, setSelectedStars] = useState([]);
  const [selectedAmenities, setSelectedAmenities] = useState([]);
  const [sort, setSort]               = useState('rating_desc');

  useEffect(() => {
    fetchAmenities().then(d => setAmenities(d.amenities)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const params = {
      city, check_in: checkIn, check_out: checkOut, guests,
      page, limit: 10, sort,
      ...(minPrice && { min_price: minPrice }),
      ...(maxPrice && { max_price: maxPrice }),
      ...(selectedStars.length && { stars: selectedStars.join(',') }),
      ...(selectedAmenities.length && { amenities: selectedAmenities.join(',') }),
    };
    fetchHotels(params)
      .then(d => { setHotels(d.hotels); setTotal(d.total); setPages(d.pages); })
      .catch(() => setError('Failed to load hotels.'))
      .finally(() => setLoading(false));
  }, [city, checkIn, checkOut, guests, page, sort, minPrice, maxPrice, selectedStars, selectedAmenities]);

  const toggleStar = (s) =>
    setSelectedStars(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]);

  const toggleAmenity = (id) =>
    setSelectedAmenities(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  const nights = checkIn && checkOut
    ? Math.max((new Date(checkOut) - new Date(checkIn)) / 86400000, 1)
    : 1;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 flex gap-6">
      {/* Sidebar filters */}
      <aside className="hidden md:block w-56 shrink-0">
        <div className="bg-white rounded-xl shadow p-4 sticky top-4 space-y-6">
          <h3 className="font-bold text-gray-700">Filters</h3>

          {/* Price */}
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Price / night</p>
            <div className="flex gap-2 items-center">
              <input type="number" placeholder="Min" value={minPrice}
                onChange={e => { setMinPrice(e.target.value); setPage(1); }}
                className="w-full border rounded px-2 py-1 text-sm" />
              <span className="text-gray-400">–</span>
              <input type="number" placeholder="Max" value={maxPrice}
                onChange={e => { setMaxPrice(e.target.value); setPage(1); }}
                className="w-full border rounded px-2 py-1 text-sm" />
            </div>
          </div>

          {/* Star rating */}
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-2">Star rating</p>
            {[5, 4, 3, 2, 1].map(s => (
              <label key={s} className="flex items-center gap-2 cursor-pointer mb-1">
                <input type="checkbox" checked={selectedStars.includes(s)}
                  onChange={() => { toggleStar(s); setPage(1); }} />
                <StarRating rating={s} size="sm" />
              </label>
            ))}
          </div>

          {/* Amenities */}
          {amenities.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-gray-600 mb-2">Amenities</p>
              {amenities.map(a => (
                <label key={a.id} className="flex items-center gap-2 cursor-pointer mb-1 text-sm text-gray-700">
                  <input type="checkbox" checked={selectedAmenities.includes(a.id)}
                    onChange={() => { toggleAmenity(a.id); setPage(1); }} />
                  {a.name}
                </label>
              ))}
            </div>
          )}
        </div>
      </aside>

      {/* Results */}
      <div className="flex-1 min-w-0">
        {/* Header row */}
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <p className="text-gray-600 text-sm">
            {loading ? 'Searching…' : `${total} propert${total === 1 ? 'y' : 'ies'} found${city ? ` in ${city}` : ''}`}
          </p>
          <div className="flex items-center gap-2">
            <MobileFilterDrawer
              amenities={amenities}
              minPrice={minPrice} setMinPrice={v => { setMinPrice(v); setPage(1); }}
              maxPrice={maxPrice} setMaxPrice={v => { setMaxPrice(v); setPage(1); }}
              selectedStars={selectedStars} toggleStar={s => { toggleStar(s); setPage(1); }}
              selectedAmenities={selectedAmenities} toggleAmenity={id => { toggleAmenity(id); setPage(1); }}
              sort={sort} setSort={v => { setSort(v); setPage(1); }}
              onApply={() => setPage(1)}
            />
            <select value={sort} onChange={e => { setSort(e.target.value); setPage(1); }}
              className="hidden md:block border rounded px-3 py-1 text-sm">
              <option value="rating_desc">Top rated</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </select>
          </div>
        </div>

        {error && <p className="text-red-500 py-4">{error}</p>}
        {loading && <LoadingSpinner className="py-20" />}

        {!loading && !error && hotels.length === 0 && (
          <div className="text-center py-20 text-gray-400">
            <p className="text-5xl mb-4">🔍</p>
            <p className="text-lg">No hotels found. Try adjusting your filters.</p>
          </div>
        )}

        <div className="space-y-4">
          {hotels.map(hotel => {
            const photo = hotel.photos.find(p => p.is_primary) || hotel.photos[0];
            const totalPrice = hotel.min_price ? (hotel.min_price * nights).toFixed(0) : null;
            return (
              <Link
                key={hotel.id}
                to={`/hotels/${hotel.slug}?check_in=${checkIn}&check_out=${checkOut}&guests=${guests}`}
                className="block bg-white rounded-xl shadow hover:shadow-md transition overflow-hidden"
              >
                <div className="flex flex-col sm:flex-row">
                  <img
                    src={photo?.url || 'https://picsum.photos/seed/default/400/260'}
                    alt={hotel.name}
                    className="sm:w-56 h-44 object-cover shrink-0"
                  />
                  <div className="p-4 flex-1 flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between gap-2 flex-wrap">
                        <h2 className="font-bold text-gray-800 text-lg leading-tight">{hotel.name}</h2>
                        <div className="flex items-center gap-2">
                          <WishlistButton hotelId={hotel.id} />
                          {hotel.avg_rating && (
                            <span className="bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">
                              {hotel.avg_rating.toFixed(1)}
                            </span>
                          )}
                          <StarRating rating={hotel.star_rating} size="sm" />
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">{hotel.city}{hotel.state_province ? `, ${hotel.state_province}` : ''}, {hotel.country}</p>
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">{hotel.description}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {hotel.amenities.slice(0, 4).map(a => (
                          <span key={a.id} className="text-xs bg-blue-50 text-blue-600 rounded-full px-2 py-0.5">{a.name}</span>
                        ))}
                        {hotel.amenities.length > 4 && (
                          <span className="text-xs text-gray-400">+{hotel.amenities.length - 4} more</span>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 flex items-end justify-between">
                      <span className="text-xs text-gray-400">{nights} night{nights !== 1 ? 's' : ''}</span>
                      {hotel.min_price ? (
                        <div className="text-right">
                          <p className="text-xs text-gray-400">from</p>
                          <p className="text-xl font-bold text-blue-600">${totalPrice}</p>
                          <p className="text-xs text-gray-400">${hotel.min_price}/night</p>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Price unavailable</span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Pagination */}
        {pages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)}
                className={`px-3 py-1 rounded border text-sm ${p === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}`}>
                {p}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResultsPage;
