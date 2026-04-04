import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ToastProvider } from './components/common/Toast';
import ErrorBoundary from './components/common/ErrorBoundary';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import ProtectedRoute from './components/common/ProtectedRoute';

import LandingPage        from './pages/LandingPage';
import SearchResultsPage  from './pages/SearchResultsPage';
import HotelDetailPage    from './pages/HotelDetailPage';
import LoginPage          from './pages/auth/LoginPage';
import RegisterPage       from './pages/auth/RegisterPage';
import GuestDetailsPage   from './pages/booking/GuestDetailsPage';
import PaymentPage        from './pages/booking/PaymentPage';
import ConfirmationPage   from './pages/booking/ConfirmationPage';
import MyBookingsPage     from './pages/account/MyBookingsPage';
import BookingDetailPage  from './pages/account/BookingDetailPage';
import ProfilePage        from './pages/account/ProfilePage';
import HomePage           from './pages/HomePage';
import AdminDashboard     from './pages/admin/AdminDashboard';
import WishlistPage       from './pages/account/WishlistPage';
import NotFoundPage       from './pages/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ToastProvider>
      <ErrorBoundary>
        <BrowserRouter>
          <div className="flex flex-col min-h-screen">
            <Navbar />
            <div className="flex-1">
              <Routes>
                {/* Discovery */}
                <Route path="/"             element={<LandingPage />} />
                <Route path="/search"       element={<SearchResultsPage />} />
                <Route path="/hotels/:slug" element={<HotelDetailPage />} />

                {/* Auth */}
                <Route path="/auth/login"    element={<LoginPage />} />
                <Route path="/auth/register" element={<RegisterPage />} />

                {/* Booking flow (protected) */}
                <Route path="/booking/details"             element={<ProtectedRoute><GuestDetailsPage /></ProtectedRoute>} />
                <Route path="/booking/payment"             element={<ProtectedRoute><PaymentPage /></ProtectedRoute>} />
                <Route path="/booking/confirmation/:bookingId" element={<ProtectedRoute><ConfirmationPage /></ProtectedRoute>} />

                {/* Account (protected) */}
                <Route path="/account/bookings"          element={<ProtectedRoute><MyBookingsPage /></ProtectedRoute>} />
                <Route path="/account/bookings/:bookingId" element={<ProtectedRoute><BookingDetailPage /></ProtectedRoute>} />
                <Route path="/account/wishlist"            element={<ProtectedRoute><WishlistPage /></ProtectedRoute>} />
                <Route path="/account/profile"             element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

                {/* Admin dashboard (hotel_admin / superadmin) */}
                <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />

                {/* Legacy hotel management */}
                <Route path="/manage" element={<HomePage />} />

                {/* 404 catch-all */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </div>
            <Footer />
          </div>
        </BrowserRouter>
      </ErrorBoundary>
    </ToastProvider>
  </QueryClientProvider>
);

export default App;
