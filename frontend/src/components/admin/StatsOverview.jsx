import { useQuery } from '@tanstack/react-query';
import { fetchAdminStats } from '../../api/admin';
import LoadingSpinner from '../common/LoadingSpinner';

const StatCard = ({ label, value, sub }) => (
  <div className="bg-white rounded-xl border shadow-sm p-5">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
    {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
  </div>
);

const StatsOverview = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: fetchAdminStats,
  });

  if (isLoading) return <LoadingSpinner className="py-20" />;
  if (!data) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard label="Hotels"   value={data.total_hotels} />
      <StatCard label="Rooms"    value={data.total_rooms} />
      <StatCard label="Bookings" value={data.total_bookings}
        sub={`${data.confirmed} confirmed · ${data.cancelled} cancelled`} />
      <StatCard label="Revenue"  value={`$${data.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
      <StatCard label="Reviews"  value={data.total_reviews} />
      {data.total_users != null && <StatCard label="Users" value={data.total_users} />}
    </div>
  );
};

export default StatsOverview;
