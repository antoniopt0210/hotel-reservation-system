import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { fetchHotel, fetchHotelRooms } from '../../api/hotels';
import useAuthStore from '../../store/authStore';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import PriceBreakdown from '../../components/booking/PriceBreakdown';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const GuestDetailsPage = () => {
  const [searchParams] = useSearchParams();
  const navigate       = useNavigate();
  const { user }       = useAuthStore();

  const roomId    = searchParams.get('room_id');
  const hotelSlug = searchParams.get('hotel_slug');
  const checkIn   = searchParams.get('check_in');
  const checkOut  = searchParams.get('check_out');
  const numGuests = Number(searchParams.get('guests') || 1);

  const [room, setRoom]     = useState(null);
  const [hotel, setHotel]   = useState(null);
  const [loading, setLoading] = useState(true);

  const nights = checkIn && checkOut
    ? Math.max((new Date(checkOut) - new Date(checkIn)) / 86400000, 1)
    : 1;

  const pricing = room ? {
    nightly_rate: room.base_price_usd,
    nights,
    subtotal:  parseFloat((room.base_price_usd * nights).toFixed(2)),
    tax_rate:  0.10,
    tax:       parseFloat((room.base_price_usd * nights * 0.10).toFixed(2)),
    total:     parseFloat((room.base_price_usd * nights * 1.10).toFixed(2)),
  } : null;

  const [form, setForm] = useState({
    first_name:       user?.first_name || '',
    last_name:        user?.last_name  || '',
    email:            user?.email      || '',
    special_requests: '',
  });

  useEffect(() => {
    if (!hotelSlug || !roomId) return;
    Promise.all([fetchHotel(hotelSlug), fetchHotelRooms(hotelSlug)])
      .then(([hotelData, roomData]) => {
        setHotel(hotelData.hotel);
        const found = roomData.rooms.find(r => r.id === roomId);
        setRoom(found || null);
      })
      .finally(() => setLoading(false));
  }, [hotelSlug, roomId]);

  const set = f => e => setForm(p => ({ ...p, [f]: e.target.value }));

  const handleContinue = (e) => {
    e.preventDefault();
    const params = new URLSearchParams({
      room_id: roomId, hotel_slug: hotelSlug,
      check_in: checkIn, check_out: checkOut, guests: numGuests,
      first_name: form.first_name, last_name: form.last_name,
      email: form.email, special_requests: form.special_requests,
    });
    navigate(`/booking/payment?${params}`);
  };

  if (loading) return <LoadingSpinner className="py-32" size="lg" />;

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <span className="text-blue-600 font-medium">1 Guest details</span>
        <span>›</span><span>2 Payment</span>
        <span>›</span><span>3 Confirmation</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
        {/* Form */}
        <form onSubmit={handleContinue} className="md:col-span-3 space-y-4">
          <h1 className="text-2xl font-bold text-gray-800">Your details</h1>
          <div className="grid grid-cols-2 gap-3">
            <Input id="first_name" label="First name" value={form.first_name} onChange={set('first_name')} required />
            <Input id="last_name"  label="Last name"  value={form.last_name}  onChange={set('last_name')}  required />
          </div>
          <Input id="email" label="Email" type="email" value={form.email} onChange={set('email')} required />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Special requests (optional)</label>
            <textarea rows={3} value={form.special_requests} onChange={set('special_requests')}
              placeholder="Early check-in, dietary requirements, etc."
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <Button type="submit" className="w-full mt-2">Continue to Payment</Button>
        </form>

        {/* Summary */}
        <div className="md:col-span-2 space-y-4">
          {hotel && room && (
            <div className="bg-white border rounded-xl shadow p-4 text-sm space-y-2">
              <p className="font-bold text-gray-800">{hotel.name}</p>
              <p className="text-gray-500">{room.name}</p>
              <p className="text-gray-500">{checkIn} → {checkOut} · {numGuests} guest{numGuests > 1 ? 's' : ''}</p>
            </div>
          )}
          {pricing && <PriceBreakdown pricing={pricing} />}
        </div>
      </div>
    </div>
  );
};

export default GuestDetailsPage;
