import { useState } from 'react';
import useAuthStore from '../../store/authStore';
import StatsOverview from '../../components/admin/StatsOverview';
import BookingsTable from '../../components/admin/BookingsTable';
import UsersTable from '../../components/admin/UsersTable';

const TABS = [
  { key: 'overview', label: 'Overview' },
  { key: 'bookings', label: 'Bookings' },
  { key: 'users',    label: 'Users' },
];

const AdminDashboard = () => {
  const { user } = useAuthStore();
  const [tab, setTab] = useState('overview');

  const isSuperadmin = user?.role === 'superadmin';
  const tabs = isSuperadmin ? TABS : TABS.filter(t => t.key !== 'users');

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Admin Dashboard</h1>

      {/* Tab bar */}
      <div className="flex gap-1 border-b mb-6">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === t.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && <StatsOverview />}
      {tab === 'bookings' && <BookingsTable />}
      {tab === 'users' && isSuperadmin && <UsersTable />}
    </div>
  );
};

export default AdminDashboard;
