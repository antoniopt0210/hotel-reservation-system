import React, { useState, useEffect } from "react";

// Define the API endpoint URL for your Python backend
// This should be the address where your Flask app is running
const API_BASE_URL = 'https://hotel-reservation-system-backend-aeqb.onrender.com/api/reservations';

const App = () => {
    // Reservation state variables
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [birthday, setBirthday] = useState('');
    const [checkIn, setCheckIn] = useState('');
    const [checkOut, setCheckOut] = useState('');
    const [roomType, setRoomType] = useState('King bed');
    const [extraInfo, setExtraInfo] = useState('');
    
    // State variable to store reservations fetched from the backend
    const [reservations, setReservations] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Function to fetch all reservations from the backend
    const fetchReservations = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(API_BASE_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setReservations(data.reservations);
        } catch (e) {
            console.error("Failed to fetch reservations:", e);
            setError("Failed to load reservations. Please check the backend server.");
        } finally {
            setIsLoading(false);
        }
    };

    // useEffect hook to fetch data when the component first mounts
    useEffect(() => {
        fetchReservations();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault(); 
        
        // Corrected to use snake_case to match the Python backend
        const newReservation = {
            first_name: firstName,
            last_name: lastName,
            birthday: birthday || null, // Ensure birthday is not an empty string
            check_in_date: checkIn,
            check_out_date: checkOut,
            room_type: roomType,
            extra_info: extraInfo,
            status: "Booked",
            created_at: new Date().toISOString()
        };

        try {
            const response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newReservation),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Reservation created successfully:", result);
            
            // Re-fetch the reservations to update the list
            fetchReservations();
            
            // Clear the form fields
            setFirstName('');
            setLastName('');
            setBirthday('');
            setCheckIn('');
            setCheckOut('');
            setRoomType('King bed');
            setExtraInfo('');

        } catch (e) {
            console.error("Error creating reservation:", e);
            setErrorMessage(e.error)
        }
    };
    
    const handleUpdateStatus = async (reservationId, newStatus) => {
        try {
            const response = await fetch(`${API_BASE_URL}/${reservationId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Re-fetch the reservations to update the list
            fetchReservations();
        } catch (e) {
            console.error("Error updating reservation:", e);
        }
    };

    const handleDeleteReservation = async (reservationId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/${reservationId}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Re-fetch the reservations to update the list
            fetchReservations();
        } catch (e) {
            console.error("Error deleting reservation:", e);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <header className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-800">Hotel Management System</h1>
            </header>
            
            <main className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <section className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-700">Book a Reservation</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <label htmlFor="firstName" className="block text-gray-600">First Name:</label>
                        <input type="text" id="firstName" name="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" />
                        
                        <label htmlFor="lastName" className="block text-gray-600">Last Name:</label>
                        <input type="text" id="lastName" name="lastName" value={lastName} onChange={(e) => setLastName(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" />
                        
                        <label htmlFor="birthday" className="block text-gray-600">Birthday:</label>
                        <input type="date" id="birthday" name="birthday" value={birthday} onChange={(e) => setBirthday(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" />
                        
                        <label htmlFor="checkIn" className="block text-gray-600">Check-in Date:</label>
                        <input type="date" id="checkIn" name="checkIn" value={checkIn} onChange={(e) => setCheckIn(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" />
                        
                        <label htmlFor="checkOut" className="block text-gray-600">Check-out Date:</label>
                        <input type="date" id="checkOut" name="checkOut" value={checkOut} onChange={(e) => setCheckOut(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" />
                        
                        <label htmlFor="roomType" className="block text-gray-600">Room Type:</label>
                        <select id="roomType" name="roomType" value={roomType} onChange={(e) => setRoomType(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300">
                            <option value="King bed">King bed</option>
                            <option value="Queen bed">Queen bed</option>
                            <option value="Double beds">Double beds</option>
                        </select>
                        
                        <label htmlFor="extraInfo" className="block text-gray-600">Extra Information:</label>
                        <textarea id="extraInfo" name="extraInfo" value={extraInfo} onChange={(e) => setExtraInfo(e.target.value)} className="w-full px-4 py-2 border rounded-md focus:ring focus:ring-blue-300" rows="3"></textarea>
                        
                        <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-300">
                            Book Reservation
                        </button>
                    </form>
                </section>
                
                <section className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-700">Current Reservations</h2>
                    {isLoading && <p>Loading reservations...</p>}
                    {error && <p className="text-red-500">{error}</p>}
                    {!isLoading && !error && reservations.length === 0 && (
                        <p className="text-gray-500">No reservations found.</p>
                    )}
                    
                    <div className="space-y-4">
                        {reservations.map(reservation => (
                            <div key={reservation.id} className="p-4 border rounded-lg shadow-sm">
                                <p><strong>Name:</strong> {reservation.first_name} {reservation.last_name}</p>
                                <p><strong>Room Type:</strong> {reservation.room_type}</p>
                                <p><strong>Check-in:</strong> {reservation.check_in_date}</p>
                                <p><strong>Check-out:</strong> {reservation.check_out_date}</p>
                                <p><strong>Status:</strong> {reservation.status}</p>
                                <div className="mt-2 space-x-2">
                                    {reservation.status === 'Booked' && (
                                        <>
                                            <button onClick={() => handleUpdateStatus(reservation.id, 'Checked-In')} className="bg-green-500 text-white py-1 px-3 rounded-md hover:bg-green-600">Check-In</button>
                                            <button onClick={() => handleUpdateStatus(reservation.id, 'Canceled')} className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600">Cancel</button>
                                        </>
                                    )}
                                    {reservation.status === 'Checked-In' && (
                                        <button onClick={() => handleUpdateStatus(reservation.id, 'Checked-Out')} className="bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600">Check-Out</button>
                                    )}
                                    <button onClick={() => handleDeleteReservation(reservation.id)} className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600">Delete</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
};

export default App;
