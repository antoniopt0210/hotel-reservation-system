import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchBooking } from '../../api/bookings';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Button from '../../components/common/Button';

const ConfirmationPage = () => {
  const { bookingId }         = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooking(bookingId)
      .then(d => setBooking(d.booking))
      .finally(() => setLoading(false));
  }, [bookingId]);

  if (loading) return <LoadingSpinner className="py-32" size="lg" />;

  const nights = booking
    ? Math.max((new Date(booking.check_out_date) - new Date(booking.check_in_date)) / 86400000, 1)
    : 0;

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      {/* Breadcrumb */}
      <div className="flex items-center justify-center gap-2 text-sm text-gray-400 mb-8">
        <span>1 Guest details</span>
        <span>›</span><span>2 Payment</span>
        <span>›</span><span className="text-blue-600 font-medium">3 Confirmation</span>
      </div>

      <div className="text-5xl mb-4">🎉</div>
      <h1 className="text-3xl font-bold text-gray-800 mb-2">You're all booked!</h1>
      <p className="text-gray-500 mb-8">A confirmation has been sent to {booking?.guest_email}.</p>

      {booking && (
        <div className="bg-white border rounded-xl shadow p-6 text-left space-y-3 mb-8">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Booking reference</span>
            <span className="font-mono font-bold text-blue-600 text-lg">
              {booking.id.slice(0, 8).toUpperCase()}
            </span>
          </div>
          <hr />
          <Row label="Hotel"     value={booking.hotel_name} />
          <Row label="Room"      value={booking.room_name} />
          <Row label="Check-in"  value={booking.check_in_date} />
          <Row label="Check-out" value={booking.check_out_date} />
          <Row label="Nights"    value={nights} />
          <Row label="Guests"    value={booking.num_guests} />
          <hr />
          <Row label="Total paid" value={`$${booking.total_price_usd.toFixed(2)}`} bold />
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link to="/account/bookings">
          <Button variant="secondary">View My Bookings</Button>
        </Link>
        <Link to="/">
          <Button>Book Another Stay</Button>
        </Link>
      </div>
    </div>
  );
};

const Row = ({ label, value, bold = false }) => (
  <div className="flex justify-between text-sm">
    <span className="text-gray-500">{label}</span>
    <span className={bold ? 'font-bold text-gray-800' : 'text-gray-800'}>{value}</span>
  </div>
);

export default ConfirmationPage;
