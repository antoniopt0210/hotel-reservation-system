import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchBooking, cancelBooking } from '../../api/bookings';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Button from '../../components/common/Button';
import { useToast } from '../../components/common/Toast';

const BookingDetailPage = () => {
  const { bookingId } = useParams();
  const navigate      = useNavigate();
  const toast         = useToast();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooking(bookingId)
      .then(d => setBooking(d.booking))
      .finally(() => setLoading(false));
  }, [bookingId]);

  const handleCancel = async () => {
    if (!window.confirm('Cancel this booking?')) return;
    try {
      await cancelBooking(bookingId);
      toast('Booking cancelled successfully', 'success');
      navigate('/account/bookings');
    } catch (err) {
      toast(err.response?.data?.error || 'Cancellation failed.', 'error');
    }
  };

  if (loading) return <LoadingSpinner className="py-32" size="lg" />;
  if (!booking) return <p className="text-center py-20 text-gray-500">Booking not found.</p>;

  const nights = Math.max(
    (new Date(booking.check_out_date) - new Date(booking.check_in_date)) / 86400000, 1
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="mb-6">
        <Link to="/account/bookings" className="text-sm text-blue-600 hover:underline">← My Bookings</Link>
      </div>

      <div className="bg-white border rounded-xl shadow p-6 space-y-4">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-xl font-bold text-gray-800">{booking.hotel_name}</h1>
            <p className="text-gray-500 text-sm">{booking.room_name}</p>
          </div>
          <span className="font-mono font-bold text-blue-600">
            {booking.id.slice(0, 8).toUpperCase()}
          </span>
        </div>

        <hr />

        <div className="grid grid-cols-2 gap-4 text-sm">
          <Info label="Check-in"   value={booking.check_in_date} />
          <Info label="Check-out"  value={booking.check_out_date} />
          <Info label="Nights"     value={nights} />
          <Info label="Guests"     value={booking.num_guests} />
          <Info label="Status"     value={booking.status.replace('_', ' ')} />
          <Info label="Total paid" value={`$${booking.total_price_usd.toFixed(2)}`} />
        </div>

        {booking.special_requests && (
          <div className="bg-gray-50 rounded p-3 text-sm text-gray-600">
            <p className="font-medium text-gray-700 mb-1">Special requests</p>
            {booking.special_requests}
          </div>
        )}

        {/* Review prompt */}
        {(booking.status === 'checked_out' || booking.status === 'confirmed') && booking.hotel_slug && (
          <Link
            to={`/hotels/${booking.hotel_slug}`}
            className="block bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-700 hover:bg-blue-100 transition"
          >
            How was your stay? Leave a review →
          </Link>
        )}

        <div className="flex gap-3 pt-2 flex-wrap">
          {booking.hotel_slug && (
            <Link to={`/hotels/${booking.hotel_slug}`}>
              <Button variant="secondary" size="sm">View Hotel</Button>
            </Link>
          )}
          {booking.status === 'confirmed' && (
            <Button variant="danger" size="sm" onClick={handleCancel}>
              Cancel Booking
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

const Info = ({ label, value }) => (
  <div>
    <p className="text-xs text-gray-400">{label}</p>
    <p className="font-medium text-gray-800">{value}</p>
  </div>
);

export default BookingDetailPage;
