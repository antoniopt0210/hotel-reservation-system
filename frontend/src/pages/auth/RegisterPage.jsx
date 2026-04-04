import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../../api/auth';
import useAuthStore from '../../store/authStore';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

const RegisterPage = () => {
  const navigate    = useNavigate();
  const { setAuth } = useAuthStore();

  const [form, setForm]     = useState({ email: '', password: '', first_name: '', last_name: '', phone: '' });
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    try {
      const data = await register(form);
      setAuth(data.user, data.access_token);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 px-4">
      <div className="bg-white rounded-xl shadow-md p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">Create your account</h1>

        {error && (
          <p className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded p-2 text-center">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input id="first_name" label="First Name" value={form.first_name} onChange={set('first_name')} required />
            <Input id="last_name"  label="Last Name"  value={form.last_name}  onChange={set('last_name')}  required />
          </div>
          <Input id="email"    label="Email"    type="email"    value={form.email}    onChange={set('email')}    required />
          <Input id="phone"    label="Phone"    type="tel"      value={form.phone}    onChange={set('phone')} />
          <Input id="password" label="Password" type="password" value={form.password} onChange={set('password')} required />
          <p className="text-xs text-gray-400 -mt-2">Minimum 8 characters.</p>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Creating account…' : 'Create Account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/auth/login" className="text-blue-600 hover:underline font-medium">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
