import { Navigate, useLocation } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const ProtectedRoute = ({ children }) => {
  const { token }  = useAuthStore();
  const location   = useLocation();

  if (!token) {
    return <Navigate to="/auth/login" state={{ from: location.pathname }} replace />;
  }
  return children;
};

export default ProtectedRoute;
