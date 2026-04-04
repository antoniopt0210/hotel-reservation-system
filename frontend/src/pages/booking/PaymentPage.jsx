import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { createPaymentIntent, confirmBooking, testConfirmBooking } from '../../api/bookings';
import PriceBreakdown from '../../components/booking/PriceBreakdown';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || '');

const PaymentPage = () => {
  const [searchParams] = useSearchParams();
  const navigate       = useNavigate();

  const roomId    = searchParams.get('room_id');
  const checkIn   = searchParams.get('check_in');
  const checkOut  = searchParams.get('check_out');
  const guests    = Number(searchParams.get('guests') || 1);
  const firstName = searchParams.get('first_name');
  const lastName  = searchParams.get('last_name');
  const email     = searchParams.get('email');
  const requests  = searchParams.get('special_requests') || '';

  const [intentData, setIntentData] = useState(null);
  const [pageLoading, setPageLoading] = useState(true);
  const [submitting, setSubmitting]   = useState(false);
  const [error, setError]             = useState('');

  const cardRef     = useRef(null);
  const stripeRef   = useRef(null);
  const cardElRef   = useRef(null);

  // Step 1 — fetch PaymentIntent from backend
  useEffect(() => {
    if (!roomId || !checkIn || !checkOut) return;
    createPaymentIntent(roomId, checkIn, checkOut)
      .then(setIntentData)
      .catch(err => setError(err.response?.data?.error || 'Could not initialise payment.'))
      .finally(() => setPageLoading(false));
  }, [roomId, checkIn, checkOut]);

  // Step 2 — mount Stripe Card Element once intent is ready
  useEffect(() => {
    if (!intentData || !cardRef.current) return;

    stripePromise.then(stripe => {
      if (!stripe) return;
      stripeRef.current = stripe;

      const elements = stripe.elements();
      const card = elements.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#374151',
            fontFamily: 'ui-sans-serif, system-ui, sans-serif',
            '::placeholder': { color: '#9ca3af' },
          },
          invalid: { color: '#ef4444' },
        },
      });
      card.mount(cardRef.current);
      cardElRef.current = card;
    });

    return () => { cardElRef.current?.destroy(); };
  }, [intentData]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!stripeRef.current || !cardElRef.current) return;
    setError('');
    setSubmitting(true);

    const result = await stripeRef.current.confirmCardPayment(intentData.client_secret, {
      payment_method: { card: cardElRef.current },
    });

    if (result.error) {
      setError(result.error.message);
      setSubmitting(false);
      return;
    }

    try {
      const data = await confirmBooking({
        payment_intent_id: intentData.payment_intent_id,
        room_id:           roomId,
        check_in:          checkIn,
        check_out:         checkOut,
        first_name:        firstName,
        last_name:         lastName,
        email,
        num_guests:        guests,
        special_requests:  requests,
      });
      navigate(`/booking/confirmation/${data.booking.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Booking confirmation failed. Please contact support.');
      setSubmitting(false);
    }
  };

  const handleTestBooking = async () => {
    setError('');
    setSubmitting(true);
    try {
      const data = await testConfirmBooking({
        room_id:          roomId,
        check_in:         checkIn,
        check_out:        checkOut,
        first_name:       firstName,
        last_name:        lastName,
        email,
        num_guests:       guests,
        special_requests: requests,
      });
      navigate(`/booking/confirmation/${data.booking.id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Test booking failed.');
      setSubmitting(false);
    }
  };

  if (pageLoading) return <LoadingSpinner className="py-32" size="lg" />;

  if (error && !intentData) return (
    <div className="max-w-xl mx-auto px-4 py-20 text-center">
      <p className="text-red-500 mb-4">{error}</p>
      <div className="flex flex-col gap-3 items-center">
        <Button variant="secondary" onClick={() => navigate(-1)}>Go back</Button>
        <p className="text-sm text-gray-400">Or skip payment entirely:</p>
        <Button variant="success" onClick={handleTestBooking} disabled={submitting}>
          {submitting ? 'Booking...' : 'Book Without Payment (Test Mode)'}
        </Button>
      </div>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-400 mb-6">
        <span>1 Guest details</span>
        <span>›</span>
        <span className="text-blue-600 font-medium">2 Payment</span>
        <span>›</span>
        <span>3 Confirmation</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
        {/* Payment form */}
        <form onSubmit={handleSubmit} className="md:col-span-3 space-y-4">
          <h1 className="text-2xl font-bold text-gray-800">Payment</h1>

          {/* Test mode hint */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm">
            <p className="font-semibold text-yellow-800 mb-1">Test Mode</p>
            <p className="text-yellow-700">
              Use card <span className="font-mono font-bold">4242 4242 4242 4242</span>,
              any future expiry, any CVC & ZIP.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Card details</label>
            <div
              ref={cardRef}
              className="border border-gray-300 rounded-md px-4 py-3 bg-white min-h-[44px]"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">
              {error}
            </p>
          )}

          <p className="text-xs text-gray-400">
            Your payment is secured by Stripe. We never store your card details.
          </p>

          <Button type="submit" className="w-full" disabled={submitting || !intentData}>
            {submitting ? 'Processing...' : `Pay $${intentData?.pricing?.total?.toFixed(2) ?? '...'}`}
          </Button>

          {/* Divider */}
          <div className="flex items-center gap-3 py-1">
            <div className="flex-1 border-t" />
            <span className="text-xs text-gray-400">OR</span>
            <div className="flex-1 border-t" />
          </div>

          {/* Skip payment button */}
          <Button
            type="button"
            variant="secondary"
            className="w-full"
            disabled={submitting}
            onClick={handleTestBooking}
          >
            {submitting ? 'Booking...' : 'Skip Payment (Test Mode)'}
          </Button>
        </form>

        {/* Summary sidebar */}
        <div className="md:col-span-2 space-y-4">
          {intentData?.hotel && intentData?.room && (
            <div className="bg-white border rounded-xl shadow p-4 text-sm space-y-2">
              <p className="font-bold text-gray-800">{intentData.hotel.name}</p>
              <p className="text-gray-500">{intentData.room.name}</p>
              <p className="text-gray-500">{checkIn} → {checkOut}</p>
            </div>
          )}
          {intentData?.pricing && <PriceBreakdown pricing={intentData.pricing} />}
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
