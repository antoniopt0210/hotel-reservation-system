import { Link } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const Navbar = () => {
  const { user, clearAuth } = useAuthStore();

  return (
    <nav className="bg-blue-700 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold tracking-tight hover:opacity-90">
          StayEasy
        </Link>

        <div className="flex items-center gap-4 text-sm">
          {user ? (
            <>
              <span className="opacity-80">Hi, {user.first_name}</span>
              <Link to="/account/wishlist" className="hover:underline">
                Wishlist
              </Link>
              <Link to="/account/bookings" className="hover:underline">
                My Bookings
              </Link>
              {(user.role === 'hotel_admin' || user.role === 'superadmin') && (
                <Link to="/admin" className="hover:underline">
                  Admin
                </Link>
              )}
              <button onClick={clearAuth} className="hover:underline">
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link to="/auth/login" className="hover:underline">
                Sign In
              </Link>
              <Link
                to="/auth/register"
                className="bg-white text-blue-700 font-semibold px-3 py-1 rounded-md hover:bg-gray-100"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
