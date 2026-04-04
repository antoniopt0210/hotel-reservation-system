import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchMyBookings, cancelBooking } from '../../api/bookings';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Button from '../../components/common/Button';

const STATUS_STYLES = {
  confirmed:   'bg-green-100 text-green-700',
  checked_in:  'bg-blue-100 text-blue-700',
  checked_out: 'bg-gray-100 text-gray-600',
  cancelled:   'bg-red-100 text-red-600',
  refunded:    'bg-yellow-100 text-yellow-700',
};

const MyBookingsPage = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');

  const load = () => {
    setLoading(true);
    fetchMyBookings()
      .then(d => setBookings(d.bookings))
      .catch(() => setError('Failed to load bookings.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await cancelBooking(id);
      load();
    } catch (err) {
      alert(err.response?.data?.error || 'Cancellation failed.');
    }
  };

  if (loading) return <LoadingSpinner className="py-20" />;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Bookings</h1>

      {error && <p className="text-red-500">{error}</p>}

      {!loading && bookings.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          <p className="text-5xl mb-4">🛏</p>
          <p className="text-lg mb-4">No bookings yet.</p>
          <Link to="/"><Button>Find a hotel</Button></Link>
        </div>
      )}

      <div className="space-y-4">
        {bookings.map(b => {
          const nights = Math.max(
            (new Date(b.check_out_date) - new Date(b.check_in_date)) / 86400000, 1
          );
          return (
            <div key={b.id} className="bg-white border rounded-xl shadow-sm p-5">
              <div className="flex items-start justify-between flex-wrap gap-2">
                <div>
                  <p className="font-bold text-gray-800">{b.hotel_name}</p>
                  <p className="text-sm text-gray-500">{b.room_name}</p>
                </div>
                <span className={`text-xs font-semibold px-2 py-1 rounded-full ${STATUS_STYLES[b.status] || 'bg-gray-100 text-gray-600'}`}>
                  {b.status.replace('_', ' ')}
                </span>
              </div>
              <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm text-gray-600">
                <div><p className="text-xs text-gray-400">Check-in</p>{b.check_in_date}</div>
                <div><p className="text-xs text-gray-400">Check-out</p>{b.check_out_date}</div>
                <div><p className="text-xs text-gray-400">Nights</p>{nights}</div>
                <div><p className="text-xs text-gray-400">Total</p>${b.total_price_usd.toFixed(2)}</div>
              </div>
              <div className="mt-4 flex gap-2 flex-wrap">
                <Link to={`/account/bookings/${b.id}`}>
                  <Button variant="secondary" size="sm">View Details</Button>
                </Link>
                {b.status === 'confirmed' && (
                  <Button variant="danger" size="sm" onClick={() => handleCancel(b.id)}>
                    Cancel
                  </Button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MyBookingsPage;
