import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AuthDrawer({ isOpen, onClose }) {
    const [activeTab, setActiveTab] = useState('login');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Login State
    const [loginData, setLoginData] = useState({ email: '', password: '' });

    // Register State
    const [registerData, setRegisterData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        firstName: '',
        lastName: '',
    });

    const { login, register } = useAuth();
    const navigate = useNavigate();

    if (!isOpen) return null;

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(loginData.email, loginData.password);
            onClose();
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    const handleRegisterSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (registerData.password !== registerData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        setLoading(true);
        try {
            await register(registerData.email, registerData.password, registerData.firstName, registerData.lastName);
            onClose();
            navigate('/dashboard');
        } catch (err) {
            let errorMessage = 'Registration failed';
            if (err.response?.data) {
                const data = err.response.data;
                if (data.email) errorMessage = data.email;
                else if (data.detail) errorMessage = data.detail;
            }
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-y-0 right-0 w-full md:w-[400px] z-50 glass-card !rounded-none !rounded-l-xl border-l border-black/10 dark:border-white/20 p-8 flex flex-col animate-slide-in-right">
            {/* Close Button */}
            <button
                onClick={onClose}
                className="absolute top-6 right-6 p-2 hover:bg-white/10 rounded-full transition-colors"
                aria-label="Close"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>

            {/* Brand Header - Fixed */}
            <div className="pt-10 px-2 text-center mb-8">
                <h1 className="text-4xl font-display font-bold text-cosmic-cyan">
                    DevScaffold
                </h1>
            </div>

            <div className="flex-1 overflow-y-auto overflow-x-hidden px-2 custom-scrollbar">

                {/* Tab Switcher */}
                <div className="flex p-1 bg-white/5 rounded-lg mb-8 border border-black/10 dark:border-white/10">
                    <button
                        onClick={() => { setActiveTab('login'); setError(''); }}
                        className={`flex-1 py-2 rounded-md font-medium transition-all ${activeTab === 'login' ? 'bg-white/10 text-cosmic-cyan' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        Login
                    </button>
                    <button
                        onClick={() => { setActiveTab('register'); setError(''); }}
                        className={`flex-1 py-2 rounded-md font-medium transition-all ${activeTab === 'register' ? 'bg-white/10 text-cosmic-cyan' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        Register
                    </button>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6 text-sm">
                        {error}
                    </div>
                )}

                {activeTab === 'login' ? (
                    /* Login Form */
                    <form onSubmit={handleLoginSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium mb-2">Email</label>
                            <input
                                type="email"
                                value={loginData.email}
                                onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                                className="input-field w-full"
                                placeholder="you@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Password</label>
                            <input
                                type="password"
                                value={loginData.password}
                                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                                className="input-field w-full"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="neon-button w-full disabled:opacity-50"
                        >
                            {loading ? 'Logging in...' : 'Log In'}
                        </button>
                    </form>
                ) : (
                    /* Register Form */
                    <form onSubmit={handleRegisterSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">First Name</label>
                                <input
                                    type="text"
                                    value={registerData.firstName}
                                    onChange={(e) => setRegisterData({ ...registerData, firstName: e.target.value })}
                                    className="input-field w-full text-sm"
                                    placeholder="John"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Last Name</label>
                                <input
                                    type="text"
                                    value={registerData.lastName}
                                    onChange={(e) => setRegisterData({ ...registerData, lastName: e.target.value })}
                                    className="input-field w-full text-sm"
                                    placeholder="Doe"
                                    required
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Email</label>
                            <input
                                type="email"
                                value={registerData.email}
                                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                                className="input-field w-full"
                                placeholder="you@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Password</label>
                            <input
                                type="password"
                                value={registerData.password}
                                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                                className="input-field w-full"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Confirm Password</label>
                            <input
                                type="password"
                                value={registerData.confirmPassword}
                                onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                                className="input-field w-full"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="neon-button w-full disabled:opacity-50"
                        >
                            {loading ? 'Creating account...' : 'Register'}
                        </button>
                    </form>
                )}

                {/* GitHub OAuth Button */}
                <div className="mt-8">
                    <div className="relative mb-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="px-2 text-gray-500 bg-[rgb(var(--bg-primary))]">Or integrate with</span>
                        </div>
                    </div>
                    <button
                        onClick={() => window.location.href = 'http://localhost:8000/accounts/github/login/?process=login'}
                        className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#24292e] hover:bg-[#2c3136] text-white transition-colors"
                    >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                        </svg>
                        Continue with GitHub
                    </button>
                </div>
            </div>

            {/* Fixed Footer */}
            <div className="pb-8 mt-4 text-center text-xs text-gray-600 uppercase tracking-widest opacity-50">
                Agentic Coding
            </div>
        </div>
    );
}
