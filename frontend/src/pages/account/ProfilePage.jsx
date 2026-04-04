import { useState, useEffect } from 'react';
import useAuthStore from '../../store/authStore';
import { updateProfile } from '../../api/auth';
import { useToast } from '../../components/common/Toast';
import Button from '../../components/common/Button';

const ProfilePage = () => {
  const { user, setAuth } = useAuthStore();
  const toast = useToast();

  const [firstName, setFirstName]     = useState('');
  const [lastName, setLastName]       = useState('');
  const [phone, setPhone]             = useState('');
  const [currentPw, setCurrentPw]     = useState('');
  const [newPw, setNewPw]             = useState('');
  const [saving, setSaving]           = useState(false);

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setPhone(user.phone || '');
    }
  }, [user]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { first_name: firstName, last_name: lastName, phone };
      if (newPw) {
        payload.current_password = currentPw;
        payload.new_password = newPw;
      }
      const data = await updateProfile(payload);
      // Update zustand store with fresh user data
      const token = localStorage.getItem('access_token');
      setAuth(data.user, token);
      setCurrentPw('');
      setNewPw('');
      toast('Profile updated', 'success');
    } catch (err) {
      toast(err.response?.data?.error || 'Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Account Settings</h1>

      <form onSubmit={handleSave} className="bg-white border rounded-xl shadow p-6 space-y-5">
        {/* Basic info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First name</label>
            <input
              type="text" value={firstName} onChange={e => setFirstName(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Last name</label>
            <input
              type="text" value={lastName} onChange={e => setLastName(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email" value={user.email} disabled
            className="w-full border rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-500"
          />
          <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <input
            type="tel" value={phone} onChange={e => setPhone(e.target.value)}
            placeholder="+1 (555) 123-4567"
            className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        {/* Password change */}
        <div className="border-t pt-4">
          <h2 className="font-semibold text-gray-700 mb-3">Change Password</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current password</label>
              <input
                type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)}
                className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">New password</label>
              <input
                type="password" value={newPw} onChange={e => setNewPw(e.target.value)}
                className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>
        </div>

        <Button type="submit" className="w-full" disabled={saving}>
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </form>
    </div>
  );
};

export default ProfilePage;
