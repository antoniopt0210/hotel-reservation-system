import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchAdminBookings, updateBookingStatus } from '../../api/admin';
import LoadingSpinner from '../common/LoadingSpinner';
import Button from '../common/Button';

const STATUS_COLORS = {
  confirmed:   'bg-green-100 text-green-700',
  checked_in:  'bg-blue-100 text-blue-700',
  checked_out: 'bg-gray-100 text-gray-700',
  cancelled:   'bg-red-100 text-red-700',
  refunded:    'bg-yellow-100 text-yellow-700',
};

const BookingsTable = () => {
  const queryClient = useQueryClient();
  const [page, setPage]           = useState(1);
  const [statusFilter, setFilter] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['admin-bookings', page, statusFilter],
    queryFn: () => fetchAdminBookings({ page, per_page: 15, ...(statusFilter && { status: statusFilter }) }),
    keepPreviousData: true,
  });

  const { mutate: changeStatus } = useMutation({
    mutationFn: ({ id, status }) => updateBookingStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-bookings']);
      queryClient.invalidateQueries(['admin-stats']);
    },
  });

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {['', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'refunded'].map(s => (
          <button
            key={s}
            onClick={() => { setFilter(s); setPage(1); }}
            className={`px-3 py-1 rounded-full text-sm border transition ${
              statusFilter === s ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      {isLoading && <LoadingSpinner className="py-10" />}

      {!isLoading && data?.bookings?.length === 0 && (
        <p className="text-gray-400 py-10 text-center">No bookings found.</p>
      )}

      {!isLoading && data?.bookings?.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="py-2 pr-3">Guest</th>
                <th className="py-2 pr-3">Hotel</th>
                <th className="py-2 pr-3">Room</th>
                <th className="py-2 pr-3">Dates</th>
                <th className="py-2 pr-3">Total</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.bookings.map(b => (
                <tr key={b.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 pr-3">{b.guest_first_name} {b.guest_last_name}</td>
                  <td className="py-2 pr-3 text-gray-600">{b.hotel_name}</td>
                  <td className="py-2 pr-3 text-gray-600">{b.room_name}</td>
                  <td className="py-2 pr-3 whitespace-nowrap text-gray-600">
                    {b.check_in_date} → {b.check_out_date}
                  </td>
                  <td className="py-2 pr-3 font-medium">${b.total_price_usd}</td>
                  <td className="py-2 pr-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[b.status] || ''}`}>
                      {b.status}
                    </span>
                  </td>
                  <td className="py-2">
                    <select
                      value={b.status}
                      onChange={e => changeStatus({ id: b.id, status: e.target.value })}
                      className="border rounded px-2 py-1 text-xs"
                    >
                      {['confirmed', 'checked_in', 'checked_out', 'cancelled', 'refunded'].map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {data?.pages > 1 && (
        <div className="flex gap-2 justify-center pt-2">
          <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Prev</Button>
          <span className="text-sm text-gray-500 self-center">Page {page} of {data.pages}</span>
          <Button variant="secondary" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}>Next</Button>
        </div>
      )}
    </div>
  );
};

export default BookingsTable;
