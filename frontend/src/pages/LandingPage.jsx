import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoginPage from './LoginPage';
export default function LandingPage() {
    const navigate = useNavigate();
    const { isAuthenticated, user } = useAuth();
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
        <div className="min-h-screen text-[rgb(var(--text-primary))] transition-colors duration-500 relative overflow-x-hidden">
            {/* Backdrop for Login Drawer */}
            {isLoginOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300"
                    onClick={() => setIsLoginOpen(false)}
                />
            )}

            {/* Login Drawer */}
            <LoginPage isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />

            {/* Topbar Navigation */}
            <header className="bg-[rgb(var(--bg-secondary))] !rounded-none py-2 px-8 flex justify-between items-center sticky top-0 z-50 w-full border-x-0 border-t-0 border-b border-[rgb(var(--color-brand-separator)/0.3)]">
                <div className="flex items-center gap-4">
                    <div className="text-2xl font-display font-bold cursor-pointer" onClick={() => navigate('/')}>
                        <span className="text-brand-gradient">DevScaffold</span>
                    </div>
                </div>

                {/* Right Side: Login/Dashboard */}
                <div className="flex items-center gap-6">

                    {!isAuthenticated ? (
                        <button
                            onClick={() => setIsLoginOpen(true)}
                            className="text-label opacity-60 hover:opacity-100 transition-opacity"
                        >
                            Log In / Register
                        </button>
                    ) : (
                        <div className="flex items-center gap-4">
                            <span className="text-label opacity-30 hidden sm:block">Operator Online</span>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="w-10 h-10 rounded-full bg-cosmic-cyan flex items-center justify-center text-sm font-bold text-[rgb(var(--bg-primary))] transition-transform hover:scale-110 border-none"
                            >
                                {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase()}
                            </button>
                        </div>
                    )}
                </div>
            </header>

            {/* Hero Section */}
            <header className="pt-20 pb-12 px-6 text-center max-w-4xl mx-auto">
                <h1 className="text-hero mb-6">
                    From <span className="text-gold-solid italic">Intent</span> to <span className="text-gold-solid">Production</span>
                </h1>
                <p className="text-lead text-[rgb(var(--text-secondary))] mb-10">
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
            <div className="border-b border-[rgb(var(--color-brand-separator)/0.15)] max-w-7xl mx-auto" id="hero-separator" />

            {/* Pipeline Section */}
            <section className="py-20 px-6 max-w-7xl mx-auto">
                <h2 className="text-section text-center mb-16">
                    The 4-Stage Canonical Pipeline
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {pipelineStages.map((stage, index) => (
                        <div key={index} className="glass-2 p-8 hover:scale-105 transition-transform duration-300 border border-[rgb(var(--border-primary))]">
                            <div className="mb-6">{stage.icon}</div>
                            <h3 className="text-subtitle mb-3 text-[rgb(var(--color-primary))]">{stage.title}</h3>
                            <p className="text-body text-[rgb(var(--text-secondary))]">
                                {stage.description}
                            </p>
                        </div>
                    ))}
                </div>
            </section>
            <div className="border-b border-[rgb(var(--color-brand-separator)/0.15)] max-w-5xl mx-auto" id="pipeline-separator" />

            {/* Value Prop */}
            <section className="py-32 px-6 max-w-5xl mx-auto text-center relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none select-none">
                    <svg className="w-64 h-64 md:w-96 md:h-96 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                    </svg>
                </div>
                <div className="relative z-10">
                    <h2 className="text-section mb-8 italic">Entropy Strictly Decreases</h2>
                    <p className="text-lead text-[rgb(var(--text-secondary))] max-w-3xl mx-auto">
                        Unlike traditional LLM generation, DevScaffold uses a deterministic pipeline. Each stage validates the previous,
                        ensuring that your project architecture is solid before a single line of code is written.
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-[rgb(var(--color-brand-separator)/0.3)] text-center text-[rgb(var(--text-secondary))]">
                <p>© 2026 DevScaffold. Built for the era of Agentic Coding.</p>
            </footer>
        </div >
    );
}
