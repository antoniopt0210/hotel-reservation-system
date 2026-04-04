import { Link } from 'react-router-dom';
import Button from '../components/common/Button';

const NotFoundPage = () => (
  <div className="min-h-[60vh] flex items-center justify-center px-4">
    <div className="text-center max-w-md">
      <p className="text-7xl font-bold text-blue-600 mb-2">404</p>
      <h1 className="text-2xl font-bold text-gray-800 mb-2">Page not found</h1>
      <p className="text-gray-500 mb-6">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div className="flex gap-3 justify-center">
        <Link to="/"><Button>Go Home</Button></Link>
        <Link to="/search"><Button variant="secondary">Search Hotels</Button></Link>
      </div>
    </div>
  </div>
);

export default NotFoundPage;
