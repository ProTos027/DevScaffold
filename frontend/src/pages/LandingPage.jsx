import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoginPage from './LoginPage';
export default function LandingPage() {
    const navigate = useNavigate();
    const { isAuthenticated, user } = useAuth();
    const [isLoginOpen, setIsLoginOpen] = useState(false);

    const tourSteps = [
        {
            number: '01',
            title: 'Secure Identity',
            description: 'Authenticate via GitHub or manual credentials to persist your project history and generated assets in the cloud.',
            image: '/screenshots/step1_login.png',
            tag: 'AUTH'
        },
        {
            number: '02',
            title: 'Fuel the Factory',
            description: 'Plug in your Gemini API keys securely in the Vault to power our agentic reasoning engine.',
            image: '/screenshots/step2_keys.png',
            tag: 'SETUP'
        },
        {
            number: '03',
            title: 'Define Vision',
            description: 'Describe your idea in natural language. From simple Todo lists to complex enterprise systems.',
            image: '/screenshots/step3_prompt.png',
            tag: 'INTENT'
        },
        {
            number: '04',
            title: 'Verify Blueprint',
            description: 'Review the auto-generated Intent Spec. Refine the stack, database, and features before building.',
            image: '/screenshots/step4_spec.png',
            tag: 'VALIDATION'
        },
        {
            number: '05',
            title: 'Architecture Graph',
            description: 'Visualize the logical dependency graph and component mapping derived from your spec.',
            image: '/screenshots/step5_graph.png',
            tag: 'LOGIC'
        },
        {
            number: '06',
            title: 'Agentic Build',
            description: 'Watch the multi-agent pipeline execute folder contracts and implement source code in real-time.',
            image: '/screenshots/step6_build.png',
            tag: 'PIPELINE'
        },
        {
            number: '07',
            title: 'Own the Asset',
            description: 'Download your production-ready, clean source code zip. Zero-entropy, deterministic output.',
            image: '/screenshots/step7_source.png',
            tag: 'RESULT'
        }
    ];

    return (
        <div className="min-h-screen text-[rgb(var(--text-primary))] transition-colors duration-500 relative overflow-x-hidden">
            {/* Backdrop for Login Drawer */}
            {isLoginOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] transition-opacity duration-300"
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

            {/* Product Tour Section */}
            <section className="py-24 px-6 max-w-7xl mx-auto">
                <h2 className="text-section text-center mb-4 uppercase tracking-widest text-gold-solid">
                    The Product Tour
                </h2>
                <p className="text-center text-[rgb(var(--text-secondary))] mb-20 max-w-2xl mx-auto">
                    Experience the deterministic journey from natural language intent to clean, deployable source code.
                </p>

                <div className="space-y-32">
                    {tourSteps.map((step, index) => (
                        <div key={index} className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-12 lg:gap-16`}>
                            {/* Text Content - Smaller weight */}
                            <div className="flex-1 w-full lg:max-w-sm animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                                <div className="glass-2 p-8 lg:p-12 border border-[rgb(var(--color-primary)/0.15)] relative overflow-hidden group">
                                    {/* Subtle hover glow */}
                                    <div className="absolute inset-0 bg-gold-solid/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

                                    <div className="relative z-10 space-y-6">
                                        <div className="flex items-center gap-4">
                                            <span className="text-4xl font-display font-bold opacity-10">{step.number}</span>
                                            <span className="badge-gold">{step.tag}</span>
                                        </div>
                                        <h3 className="text-section text-gold-solid">{step.title}</h3>
                                        <p className="text-lead text-[rgb(var(--text-secondary))] leading-relaxed">
                                            {step.description}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Image Visual - Larger weight */}
                            <div className="flex-[2] w-full">
                                <div className="glass-2 p-2 relative group overflow-hidden border border-[rgb(var(--color-primary)/0.2)]">
                                    <div className="absolute inset-0 bg-gold-solid/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10" />
                                    <img
                                        src={step.image}
                                        alt={step.title}
                                        className="w-full h-auto rounded-lg shadow-2xl transition-transform duration-700 group-hover:scale-[1.02]"
                                    />
                                </div>
                            </div>
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
                    <h2 className="text-section mb-8 italic">100+ projects generated</h2>
                    <p className="text-lead text-[rgb(var(--text-secondary))] max-w-3xl mx-auto">
                        DevScaffold has successfully transformed over 100 complex intents into production-ready architectures,
                        maintaining a strictly deterministic pipeline that eliminates the "hallucination problem" of traditional LLMs.
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
