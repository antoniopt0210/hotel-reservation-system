import { useState, useEffect } from 'react';
import {
  fetchReservations,
  createReservation,
  updateReservationStatus,
  deleteReservation,
} from '../api/reservations';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';

const HomePage = () => {
  // Form state
  const [firstName, setFirstName]   = useState('');
  const [lastName, setLastName]     = useState('');
  const [birthday, setBirthday]     = useState('');
  const [checkIn, setCheckIn]       = useState('');
  const [checkOut, setCheckOut]     = useState('');
  const [roomType, setRoomType]     = useState('King bed');
  const [extraInfo, setExtraInfo]   = useState('');

  // List state
  const [reservations, setReservations] = useState([]);
  const [isLoading, setIsLoading]       = useState(true);
  const [error, setError]               = useState(null);
  const [formError, setFormError]       = useState(null);

  const loadReservations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchReservations();
      setReservations(data);
    } catch (e) {
      setError('Failed to load reservations. Please check the backend server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadReservations(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    try {
      await createReservation({
        first_name:     firstName,
        last_name:      lastName,
        birthday:       birthday || null,
        check_in_date:  checkIn,
        check_out_date: checkOut,
        room_type:      roomType,
        extra_info:     extraInfo,
        status:         'Booked',
        created_at:     new Date().toISOString(),
      });
      await loadReservations();
      setFirstName(''); setLastName(''); setBirthday('');
      setCheckIn(''); setCheckOut(''); setRoomType('King bed'); setExtraInfo('');
    } catch (e) {
      const msg = e.response?.data?.error || e.message;
      setFormError(msg);
    }
  };

  const handleUpdateStatus = async (id, status, checkInDate) => {
    try {
      await updateReservationStatus(id, status, checkInDate);
      await loadReservations();
    } catch (e) {
      console.error('Error updating reservation:', e);
    }
  };

  const handleDelete = async (id, checkInDate) => {
    try {
      await deleteReservation(id, checkInDate);
      await loadReservations();
    } catch (e) {
      console.error('Error deleting reservation:', e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <header className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800">Hotel Management System</h1>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Booking form */}
        <section className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Book a Reservation</h2>

          {formError && (
            <p className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2">
              {formError}
            </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input id="firstName" label="First Name" value={firstName}
              onChange={(e) => setFirstName(e.target.value)} required />
            <Input id="lastName" label="Last Name" value={lastName}
              onChange={(e) => setLastName(e.target.value)} required />
            <Input id="birthday" label="Birthday" type="date" value={birthday}
              onChange={(e) => setBirthday(e.target.value)} />
            <Input id="checkIn" label="Check-in Date" type="date" value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)} required />
            <Input id="checkOut" label="Check-out Date" type="date" value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)} required />

            <div className="flex flex-col gap-1">
              <label htmlFor="roomType" className="text-sm font-medium text-gray-700">
                Room Type
              </label>
              <select id="roomType" value={roomType} onChange={(e) => setRoomType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400">
                <option value="King bed">King bed</option>
                <option value="Queen bed">Queen bed</option>
                <option value="Double beds">Double beds</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="extraInfo" className="text-sm font-medium text-gray-700">
                Extra Information
              </label>
              <textarea id="extraInfo" value={extraInfo} onChange={(e) => setExtraInfo(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400" />
            </div>

            <Button type="submit" className="w-full">Book Reservation</Button>
          </form>
        </section>

        {/* Reservations list */}
        <section className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Current Reservations</h2>

          {isLoading && <LoadingSpinner className="py-8" />}
          {error && <p className="text-red-500">{error}</p>}
          {!isLoading && !error && reservations.length === 0 && (
            <p className="text-gray-500">No reservations found.</p>
          )}

          <div className="space-y-4">
            {reservations.map((r) => (
              <div key={r.id} className="p-4 border rounded-lg shadow-sm">
                <p><strong>Name:</strong> {r.first_name} {r.last_name}</p>
                <p><strong>Room Type:</strong> {r.room_type}</p>
                <p><strong>Check-in:</strong> {r.check_in_date}</p>
                <p><strong>Check-out:</strong> {r.check_out_date}</p>
                <p><strong>Status:</strong> {r.status}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {r.status === 'Booked' && (
                    <>
                      <Button size="sm" variant="success"
                        onClick={() => handleUpdateStatus(r.id, 'Checked-In', r.check_in_date)}>
                        Check-In
                      </Button>
                      <Button size="sm" variant="warning"
                        onClick={() => handleUpdateStatus(r.id, 'Canceled', r.check_in_date)}>
                        Cancel
                      </Button>
                    </>
                  )}
                  {r.status === 'Checked-In' && (
                    <Button size="sm"
                      onClick={() => handleUpdateStatus(r.id, 'Checked-Out', r.check_in_date)}>
                      Check-Out
                    </Button>
                  )}
                  <Button size="sm" variant="danger"
                    onClick={() => handleDelete(r.id, r.check_in_date)}>
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default HomePage;
