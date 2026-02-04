import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import LoginPage from './LoginPage';

export default function LandingPage() {
    const navigate = useNavigate();
    const { isAuthenticated, user } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const [isLoginOpen, setIsLoginOpen] = useState(false);

    const pipelineStages = [
        {
            title: 'Intent Spec',
            description: 'Translates your natural language idea into a structured technical specification.',
            icon: (
                <svg className="w-8 h-8 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" strokeWidth="2" />
                    <circle cx="12" cy="12" r="6" strokeWidth="2" />
                    <circle cx="12" cy="12" r="2" strokeWidth="2" />
                </svg>
            )
        },
        {
            title: 'Component Plan',
            description: 'Breaks down the spec into a logical architecture and dependency graph.',
            icon: (
                <svg className="w-8 h-8 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" strokeWidth="2" />
                    <line x1="8" y1="2" x2="8" y2="18" strokeWidth="2" />
                    <line x1="16" y1="6" x2="16" y2="22" strokeWidth="2" />
                </svg>
            )
        },
        {
            title: 'Folder Contract',
            description: 'Creates a deterministic manifesto of every file and its responsibilities.',
            icon: (
                <svg className="w-8 h-8 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            )
        },
        {
            title: 'Code Generation',
            description: 'Our agent writes clean, production-ready code following the contract.',
            icon: (
                <svg className="w-8 h-8 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
            )
        }
    ];

    return (
        <div className="min-h-screen text-gray-900 dark:text-white transition-colors duration-500 relative overflow-x-hidden">
            {/* Backdrop for Login Drawer */}
            {isLoginOpen && (
                <div
                    className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity duration-300"
                    onClick={() => setIsLoginOpen(false)}
                />
            )}

            {/* Login Drawer */}
            <LoginPage isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />

            {/* Topbar Navigation */}
            <header className="glass-card m-4 p-4 flex justify-between items-center relative max-w-7xl mx-auto">
                <div className="flex items-center gap-4">
                    <div className="text-3xl font-display font-bold cursor-pointer" onClick={() => navigate('/')}>
                        <span className="gradient-text-primary">DevScaffold</span>
                    </div>
                </div>

                {/* Right Side: Toggle + Login/Dashboard */}
                <div className="flex items-center gap-6">
                    <button
                        onClick={toggleTheme}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors group"
                        title="Toggle Theme"
                    >
                        <span className="group-hover:scale-110 transition-transform inline-block">
                            {isDark ? (
                                <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                                </svg>
                            ) : (
                                <svg className="w-6 h-6 text-cosmic-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                </svg>
                            )}
                        </span>
                    </button>

                    {!isAuthenticated ? (
                        <button
                            onClick={() => setIsLoginOpen(true)}
                            className="text-xs font-bold uppercase tracking-[0.2em] opacity-60 hover:opacity-100 transition-opacity"
                        >
                            Log In / Register
                        </button>
                    ) : (
                        <div className="flex items-center gap-4">
                            <span className="text-xs font-bold uppercase tracking-[0.2em] opacity-30 hidden sm:block">Operator Online</span>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="w-10 h-10 rounded-full bg-cosmic-cyan flex items-center justify-center text-sm font-bold text-space-900 shadow-glow-cyan/20 hover:shadow-glow-cyan/40 transition-all border-none"
                            >
                                {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase()}
                            </button>
                        </div>
                    )}
                </div>
            </header>

            {/* Hero Section */}
            <header className="pt-20 pb-12 px-6 text-center max-w-4xl mx-auto">
                <h1 className="text-5xl md:text-7xl font-display font-bold mb-6 leading-tight">
                    From <span className="gradient-text-primary italic">Intent</span> to <span className="gradient-text-secondary">Production</span>
                </h1>
                <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-10 leading-relaxed">
                    A multi-agent AI factory that builds components, APIs, and even full-stack applications with architectural precision.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                        onClick={() => isAuthenticated ? navigate('/dashboard') : setIsLoginOpen(true)}
                        className="neon-button text-lg px-10 py-4"
                    >
                        {isAuthenticated ? 'Enter Dashboard' : 'Start Building Now'}
                    </button>
                </div>
            </header>

            {/* Pipeline Section */}
            <section className="py-20 px-6 max-w-7xl mx-auto">
                <h2 className="text-3xl md:text-4xl font-display font-bold text-center mb-16">
                    The 4-Stage Canonical Pipeline
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {pipelineStages.map((stage, index) => (
                        <div key={index} className="glass-card p-8 hover:scale-105 transition-transform duration-300 border border-white/20">
                            <div className="mb-6">{stage.icon}</div>
                            <h3 className="text-xl font-bold mb-3 font-display text-cosmic-cyan">{stage.title}</h3>
                            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                                {stage.description}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Value Prop */}
            <section className="py-32 px-6 max-w-5xl mx-auto text-center relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center opacity-[0.10] dark:opacity-[0.16] pointer-events-none select-none">
                    <svg className="w-64 h-64 md:w-96 md:h-96 animate-pulse text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                    </svg>
                </div>
                <div className="relative z-10">
                    <h2 className="text-4xl md:text-5xl font-display font-bold mb-8 italic">Entropy Strictly Decreases</h2>
                    <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed max-w-3xl mx-auto">
                        Unlike traditional LLM generation, DevScaffold uses a deterministic pipeline. Each stage validates the previous,
                        ensuring that your project architecture is solid before a single line of code is written.
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-gray-200 dark:border-white/10 text-center text-gray-500">
                <p>© 2026 DevScaffold. Built for the era of Agentic Coding.</p>
            </footer>
        </div>
    );
}
