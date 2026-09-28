import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Mail, Lock, User } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useUserStore } from '../../store/user.store';
import {
  apiService,
  describeApiError,
  toStoreUser,
  DEMO_PROFILE,
  PASSWORD_MIN_LENGTH
} from '../../services/api';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface AuthPageProps {
  mode: 'login' | 'register';
}

const AuthPage: React.FC<AuthPageProps> = ({ mode }) => {
  const navigate = useNavigate();
  const { setUser, demoMode } = useUserStore();
  const isRegister = mode === 'register';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const errors: { email?: string; password?: string } = {};
    if (!EMAIL_PATTERN.test(email.trim())) {
      errors.email = 'Enter a valid email address.';
    }
    if (isRegister && password.length < PASSWORD_MIN_LENGTH) {
      errors.password = `Password must be at least ${PASSWORD_MIN_LENGTH} characters.`;
    } else if (!password) {
      errors.password = 'Enter your password.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;

    setIsSubmitting(true);
    const credentials = { email: email.trim(), password };
    try {
      if (isRegister) {
        await apiService.register({
          ...credentials,
          first_name: firstName.trim() || undefined,
          last_name: lastName.trim() || undefined
        });
      }
      // Registration signs the new user straight in
      await apiService.login(credentials);
      const me = await apiService.getMe();
      setUser(toStoreUser(me) as any);
      navigate(isRegister ? '/consent' : '/dashboard');
    } catch (err) {
      apiService.logout();
      setError(describeApiError(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const continueAsDemo = () => {
    apiService.logout();
    setUser(DEMO_PROFILE as any);
    navigate('/dashboard');
  };

  const baseInputClass =
    'w-full pr-4 py-4 rounded-2xl bg-white/5 border text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500/60 transition';
  const inputClass = `${baseInputClass} pl-12`;

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-tr from-[#020617] via-[#0f172a] to-indigo-950/20">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full bg-white/[0.03] backdrop-blur-2xl p-10 rounded-[40px] border border-white/10 shadow-2xl"
      >
        <div className="flex items-center gap-3 mb-10">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <BrainCircuit className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-black tracking-tighter text-white">MENTAL<span className="text-indigo-400">FLOW</span></span>
        </div>

        <h1 className="text-3xl font-black text-white tracking-tight mb-2">
          {isRegister ? 'Create your account' : 'Welcome back'}
        </h1>
        <p className="text-sm text-slate-500 mb-8">
          {isRegister ? 'Your progress is saved to your own private record.' : 'Sign in to continue your recovery path.'}
        </p>

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          {isRegister && (
            <div className="grid grid-cols-2 gap-3">
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  aria-label="First name"
                  placeholder="First name"
                  autoComplete="given-name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className={`${inputClass} border-white/10`}
                />
              </div>
              <input
                aria-label="Last name"
                placeholder="Last name"
                autoComplete="family-name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className={`${baseInputClass} pl-4 border-white/10`}
              />
            </div>
          )}

          <div>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                aria-label="Email"
                placeholder="Email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`${inputClass} ${fieldErrors.email ? 'border-red-500/50' : 'border-white/10'}`}
              />
            </div>
            {fieldErrors.email && <p className="mt-2 text-xs text-red-300">{fieldErrors.email}</p>}
          </div>

          <div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                aria-label="Password"
                placeholder={isRegister ? `Password (min. ${PASSWORD_MIN_LENGTH} characters)` : 'Password'}
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`${inputClass} ${fieldErrors.password ? 'border-red-500/50' : 'border-white/10'}`}
              />
            </div>
            {fieldErrors.password && <p className="mt-2 text-xs text-red-300">{fieldErrors.password}</p>}
          </div>

          {error && (
            <p role="alert" className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-200 text-sm">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 disabled:opacity-60 rounded-2xl transition-all font-black text-white shadow-xl shadow-indigo-500/20"
          >
            {isSubmitting ? 'Please wait…' : isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-500">
          {isRegister ? 'Already have an account? ' : 'New to MentalFlow? '}
          <Link to={isRegister ? '/login' : '/register'} className="text-indigo-400 font-bold hover:text-white transition">
            {isRegister ? 'Sign in' : 'Create an account'}
          </Link>
        </p>

        {demoMode && (
          <div className="mt-8 pt-6 border-t border-white/5 text-center">
            <button
              type="button"
              onClick={continueAsDemo}
              className="text-[11px] font-black uppercase tracking-widest text-slate-400 hover:text-indigo-400 transition"
            >
              Continue as demo →
            </button>
            <p className="mt-2 text-[10px] text-slate-600">Uses a shared demo account, so entries are not private.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default AuthPage;
