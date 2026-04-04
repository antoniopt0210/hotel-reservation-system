import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchAdminUsers, updateUserRole } from '../../api/admin';
import LoadingSpinner from '../common/LoadingSpinner';
import Button from '../common/Button';

const ROLE_COLORS = {
  guest:        'bg-gray-100 text-gray-600',
  hotel_admin:  'bg-purple-100 text-purple-700',
  superadmin:   'bg-red-100 text-red-700',
};

const UsersTable = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['admin-users', page],
    queryFn: () => fetchAdminUsers({ page, per_page: 20 }),
    keepPreviousData: true,
  });

  const { mutate: changeRole } = useMutation({
    mutationFn: ({ id, role }) => updateUserRole(id, role),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-users']);
      queryClient.invalidateQueries(['admin-stats']);
    },
  });

  if (isLoading) return <LoadingSpinner className="py-10" />;

  return (
    <div className="space-y-4">
      {data?.users?.length === 0 && (
        <p className="text-gray-400 py-10 text-center">No users found.</p>
      )}

      {data?.users?.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="py-2 pr-3">Name</th>
                <th className="py-2 pr-3">Email</th>
                <th className="py-2 pr-3">Role</th>
                <th className="py-2 pr-3">Joined</th>
                <th className="py-2">Change Role</th>
              </tr>
            </thead>
            <tbody>
              {data.users.map(u => (
                <tr key={u.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 pr-3">{u.first_name} {u.last_name}</td>
                  <td className="py-2 pr-3 text-gray-600">{u.email}</td>
                  <td className="py-2 pr-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ROLE_COLORS[u.role] || ''}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-2 pr-3 text-gray-500 whitespace-nowrap">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-2">
                    <select
                      value={u.role}
                      onChange={e => changeRole({ id: u.id, role: e.target.value })}
                      className="border rounded px-2 py-1 text-xs"
                    >
                      {['guest', 'hotel_admin', 'superadmin'].map(r => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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

export default UsersTable;
