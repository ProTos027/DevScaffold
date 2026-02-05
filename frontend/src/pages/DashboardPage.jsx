import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, authAPI, apiKeysAPI } from '../api/client';
import { useTheme } from '../context/ThemeContext';

export default function DashboardPage() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAPIKeysModal, setShowAPIKeysModal] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [prompt, setPrompt] = useState('');
    const [projectName, setProjectName] = useState('');
    const [geminiModel, setGeminiModel] = useState('gemini-2.5-flash');
    const [geminiApiKeyId, setGeminiApiKeyId] = useState('');
    const [geminiKeys, setGeminiKeys] = useState([]);
    const [hasKeys, setHasKeys] = useState({ gemini: false });

    // New API Keys Management State
    const [userApiKeys, setUserApiKeys] = useState([]);
    const [newKeyForm, setNewKeyForm] = useState({ provider: 'gemini', name: '', apiKey: '' });

    const { user, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        fetchProjects();
        checkGeminiKeys();

        // Handle Retry redirection from ProjectPage
        if (location.state?.retryProject) {
            const p = location.state.retryProject;
            setPrompt(p.prompt);
            setProjectName(p.name ? `${p.name} (Retry)` : '');
            setGeminiModel(p.gemini_model || 'gemini-2.5-flash');
            // Clean up state after consumption
            window.history.replaceState({}, document.title);
        }

        const interval = setInterval(() => {
            fetchProjects();
        }, 5000);

        return () => clearInterval(interval);
    }, [location]);

    const checkGeminiKeys = async () => {
        try {
            const { data } = await apiKeysAPI.list();
            const keys = Array.isArray(data) ? data : (data?.results || []);
            const geminiKeysList = keys.filter(k => k.provider === 'gemini');

            setGeminiKeys(geminiKeysList);
            setHasKeys(prev => ({ ...prev, gemini: geminiKeysList.length > 0 }));

            // Ensure our selected ID is still valid, or pick a new one
            if (geminiKeysList.length > 0) {
                const isStillValid = geminiKeysList.some(k => k.id == geminiApiKeyId);
                if (!geminiApiKeyId || !isStillValid) {
                    setGeminiApiKeyId(geminiKeysList[0].id);
                }
            } else {
                setGeminiApiKeyId('');
            }
        } catch (error) {
            console.error('Failed to check Gemini keys:', error);
        }
    };

    const fetchProjects = async () => {
        try {
            const { data } = await projectsAPI.list();
            setProjects(data.results || data);
        } catch (error) {
            console.error('Failed to fetch projects:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();

        if (!hasKeys.gemini) {
            alert('Please configure at least one Google Gemini API key first');
            openAPIKeysModal();
            return;
        }

        try {
            const response = await projectsAPI.create(prompt, geminiModel, projectName, geminiApiKeyId);
            if (response && response.data) {
                navigate(`/project/${response.data.id}`);
            } else {
                alert('Project creation returned unexpected response format');
            }
        } catch (error) {
            alert('Failed to create project: ' + (error.response?.data?.detail || error.message));
        }
    };

    const openAPIKeysModal = async () => {
        setShowAPIKeysModal(true);
        setIsSidebarOpen(false);
        try {
            const { data } = await apiKeysAPI.list();
            setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
        } catch (error) {
            console.error('Failed to load API keys');
            setUserApiKeys([]);
        }
    };

    const handleRetry = async (e, project) => {
        e.stopPropagation();
        setPrompt(project.prompt);
        setProjectName(project.name ? `${project.name} (Retry)` : '');
        setGeminiModel(project.gemini_model || 'gemini-2.5-flash');
        setIsSidebarOpen(false); // Focus on the main form
    };

    const handleTerminate = async (e, projectId) => {
        e.stopPropagation();
        if (confirm('Are you sure you want to terminate this generation?')) {
            try {
                await projectsAPI.cancel(projectId);
                fetchProjects();
            } catch (error) {
                alert('Failed to terminate: ' + (error.response?.data?.detail || error.message));
            }
        }
    };

    const handleDeleteProject = async (e, project) => {
        e.stopPropagation();
        if (confirm(`Permanently delete project "${project.name || `Project #${project.id}`}"?`)) {
            try {
                await projectsAPI.delete(project.id);
                setProjects(projects.filter(p => p.id !== project.id));
            } catch (error) {
                alert('Failed to delete project: ' + (error.response?.data?.detail || error.message));
            }
        }
    };

    const handleDownload = async (e, project) => {
        e.stopPropagation();
        try {
            const { data } = await projectsAPI.download(project.id);
            const url = window.URL.createObjectURL(new Blob([data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${project.name || `project_${project.id}`}.zip`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            alert('Failed to download project');
        }
    };

    return (
        <div className="min-h-screen relative overflow-x-hidden">
            {/* Sidebar Backdrop */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity duration-300"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <div className={`fixed inset-y-0 left-0 w-72 z-50 glass-card !rounded-none !rounded-r-xl border-r border-white/20 p-8 flex flex-col transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                {/* User Profile Info */}
                <div className="flex items-center gap-4 mb-10 pb-6 border-b border-black/10 dark:border-white/10">
                    <div className="w-12 h-12 rounded-full bg-cosmic-cyan flex items-center justify-center text-xl font-bold text-space-900">
                        {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase()}
                    </div>
                    <div>
                        <div className="font-bold text-lg truncate w-40">
                            {user?.firstName && user?.lastName ? `${user.firstName} ${user.lastName}` : (user?.firstName || user?.email)}
                        </div>
                    </div>
                </div>

                {/* Fixed Top Actions */}
                <div className="space-y-1 mb-6">
                    <button
                        onClick={() => { setIsSidebarOpen(false); }}
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-xl bg-white/10 text-cosmic-cyan font-medium"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                        </svg> New Project
                    </button>

                    <button
                        onClick={openAPIKeysModal}
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-white/5 transition-colors text-left text-sm"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                        </svg> API Keys Setup
                    </button>
                </div>

                {/* Navigation Links - Scrollable */}
                <nav className="flex-1 overflow-y-auto overflow-x-hidden pr-2 custom-scrollbar">
                    <div className="pt-2">

                        <div className="pt-8">
                            <div className="text-xs uppercase tracking-widest text-gray-500 mb-6 px-4 flex justify-between items-center">
                                <span>Past Projects</span>
                                <span className="bg-white/5 px-2 py-0.5 rounded text-[10px]">{projects.length}</span>
                            </div>
                            <div className="space-y-3">
                                {projects.map(p => (
                                    <div key={p.id} className="group flex items-center justify-between glass-card !bg-white/5 !border-white/5 hover:!border-white/20 p-2 transition-all hover:scale-[1.01]">
                                        <div
                                            onClick={() => { setIsSidebarOpen(false); navigate(`/project/${p.id}`); }}
                                            className="flex-1 cursor-pointer flex items-center gap-2 min-w-0"
                                        >
                                            <span className={`w-2 h-2 rounded-full shrink-0 ${p.status === 'completed' ? 'bg-green-500' :
                                                p.status === 'failed' ? 'bg-red-500' : 'bg-cosmic-cyan animate-pulse'
                                                }`} title={p.status} />
                                            <div className="font-bold text-xs truncate group-hover:text-cosmic-cyan transition-colors" title={p.name || `Project ${p.id}`}>
                                                {p.name || `P#${p.id}`}
                                            </div>
                                            <span className="text-[9px] text-gray-500 shrink-0">{p.progress}%</span>
                                        </div>

                                        {/* Inline Actions */}
                                        <div className="flex gap-1 items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                            {p.status === 'completed' && (
                                                <button
                                                    onClick={(e) => handleDownload(e, p)}
                                                    className="p-1.5 rounded-md bg-green-500/10 hover:bg-green-500/20 text-green-400"
                                                    title="Download ZIP"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                                    </svg>
                                                </button>
                                            )}
                                            {p.status === 'failed' && (
                                                <button
                                                    onClick={(e) => handleRetry(e, p)}
                                                    className="p-1.5 rounded-md bg-cosmic-cyan/10 hover:bg-cosmic-cyan/20 text-cosmic-cyan"
                                                    title="Retry Generation"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                                    </svg>
                                                </button>
                                            )}
                                            {p.status !== 'completed' && p.status !== 'failed' && (
                                                <button
                                                    onClick={(e) => handleTerminate(e, p.id)}
                                                    className="p-1.5 rounded-md bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-400"
                                                    title="Terminate Build"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                        <rect x="9" y="9" width="6" height="6" strokeWidth="2" />
                                                    </svg>
                                                </button>
                                            )}
                                            <button
                                                onClick={(e) => handleDeleteProject(e, p)}
                                                className="p-1.5 rounded-md bg-red-500/10 hover:bg-red-500/20 text-red-500"
                                                title="Purge Project"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ))}
                                {projects.length === 0 && (
                                    <div className="px-4 py-8 text-center text-xs text-gray-600 italic">No projects recorded.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </nav>

                {/* Bottom Actions */}
                <div className="pt-6 border-t border-black/10 dark:border-white/10 space-y-4">
                    <button onClick={toggleTheme} className="w-full flex items-center justify-between px-4 py-2 rounded-lg hover:bg-white/5 transition-colors">
                        <span className="text-sm">Theme</span>
                        <span>
                            {isDark ? (
                                <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5 text-cosmic-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                </svg>
                            )}
                        </span>
                    </button>
                    <button
                        onClick={logout}
                        className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg> Logout
                    </button>
                </div>
            </div>

            {/* Header */}
            <header className="glass-card m-4 p-4 flex justify-between items-center relative">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors group"
                        aria-label="Toggle Project Navigator"
                    >
                        <svg className="w-6 h-6 group-hover:text-cosmic-cyan transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                    <div className="text-3xl font-display font-bold cursor-pointer" onClick={() => navigate('/')}>
                        <span className="gradient-text-primary">DevScaffold</span>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <span className="hidden md:block text-xs text-gray-500 uppercase tracking-[0.2em] font-medium opacity-50">Generator</span>
                    <div className="w-8 h-8 rounded-full bg-cosmic-cyan flex items-center justify-center text-xs font-bold border border-white/20 text-space-900">
                        {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase()}
                    </div>
                </div>
            </header>

            {/* Main Content Area - Unified Command Center */}
            <main className="p-4 max-w-4xl mx-auto pt-10">
                <div className="glass-card p-12 shadow-2xl animate-fade-in relative overflow-hidden">
                    {/* Decorative Background Element */}
                    <div className="absolute -top-24 -right-24 w-64 h-64 bg-cosmic-cyan/10 rounded-full blur-3xl"></div>
                    <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-cosmic-purple/10 rounded-full blur-3xl"></div>

                    <div className="relative z-10 text-center mb-12">
                        <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">Initialize <span className="text-cosmic-cyan">Pipeline</span></h2>
                        <p className="text-gray-500 max-w-xl mx-auto">Input prompt below. Our multi-agent system will handle the architectural specification, contract derivation, and production-ready code generation.</p>
                    </div>

                    <form onSubmit={handleCreateProject} className="space-y-10 relative z-10">
                        <div className="space-y-6">
                            <div className="group">
                                <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-3 group-focus-within:text-cosmic-cyan transition-colors px-2">Title</label>
                                <input
                                    type="text"
                                    value={projectName}
                                    onChange={(e) => setProjectName(e.target.value)}
                                    className="input-field w-full text-xl py-5 px-6 !bg-white/5 border-white/5 focus:border-cosmic-cyan/50 transition-all font-display"
                                    placeholder="e.g. Banking Platform"
                                />
                            </div>

                            <div className="group">
                                <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-3 group-focus-within:text-cosmic-cyan transition-colors px-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="input-field w-full h-48 resize-none py-5 px-6 !bg-white/5 border-white/5 focus:border-cosmic-cyan/50 transition-all leading-relaxed"
                                    placeholder="Describe your vision... (e.g. Build a real estate portal with AI-driven valuation and Mapbox integration)"
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="group">
                                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-3 px-2">API Key</label>
                                    {!hasKeys.gemini ? (
                                        <button
                                            type="button"
                                            onClick={openAPIKeysModal}
                                            className="w-full py-4 rounded-2xl bg-yellow-500/5 text-yellow-500 text-sm border border-yellow-500/10 hover:bg-yellow-500/10 transition-all flex items-center justify-center gap-2 font-bold"
                                        >
                                            ⚠️ Setup API Key to Proceed
                                        </button>
                                    ) : (
                                        <select
                                            value={geminiApiKeyId}
                                            onChange={(e) => setGeminiApiKeyId(e.target.value)}
                                            className="input-field w-full py-4 px-6"
                                        >
                                            {geminiKeys.map((key) => (
                                                <option key={key.id} value={key.id} className="bg-[rgb(var(--bg-secondary))] text-[rgb(var(--text-primary))]">
                                                    Key: {key.name || `...${key.key_preview}`}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                </div>
                                <div className="group">
                                    <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-3 px-2">Model</label>
                                    <select
                                        value={geminiModel}
                                        onChange={(e) => setGeminiModel(e.target.value)}
                                        className="input-field w-full py-4 px-6"
                                    >
                                        <option value="gemini-2.5-flash" className="bg-[rgb(var(--bg-secondary))] text-[rgb(var(--text-primary))]">Gemini 2.5 Flash (Optimized)</option>
                                        <option value="gemini-2.5-pro" className="bg-[rgb(var(--bg-secondary))] text-[rgb(var(--text-primary))]">Gemini 2 Pro (Superior Reasoning)</option>
                                        <option value="gemini-1.5-pro" className="bg-[rgb(var(--bg-secondary))] text-[rgb(var(--text-primary))]">Gemini 1.5 Pro (Stability)</option>
                                        <option value="gemini-1.5-flash" className="bg-[rgb(var(--bg-secondary))] text-[rgb(var(--text-primary))]">Gemini 1.5 Flash (Latency)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="neon-button w-full py-6 text-xl mt-8 font-display font-bold shadow-glow-cyan/50 hover:shadow-glow-purple/50 transition-all uppercase tracking-widest flex items-center justify-center gap-4"
                        >
                            <svg className="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg> Generate
                        </button>
                    </form>
                </div>

                <div className="mt-12 text-center text-xs text-gray-600 uppercase tracking-[0.5em] opacity-30 select-none">
                    Entropy Strictly Decreases
                </div>
            </main>

            {/* API Keys Modal */}
            {showAPIKeysModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 z-[70]">
                    <div className="glass-card p-10 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-fade-in relative">
                        <div className="flex justify-between items-center mb-2">
                            <h2 className="text-3xl font-display font-bold">Secret <span className="text-cosmic-purple">Vault</span></h2>
                            <button onClick={() => setShowAPIKeysModal(false)} className="text-gray-400 hover:text-white transition-colors">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mb-10 uppercase tracking-widest opacity-50">Multi-Provider Key Orchestration</p>

                        {/* Add New Key Form */}
                        <div className="mb-10 p-8 bg-white/5 rounded-3xl border border-white/5 shadow-inner">
                            <h3 className="text-sm font-bold mb-6 flex items-center gap-2 text-gray-400 uppercase tracking-widest">
                                <svg className="w-4 h-4 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg> Register New Credential
                            </h3>
                            <form onSubmit={async (e) => {
                                e.preventDefault();
                                try {
                                    await apiKeysAPI.create(newKeyForm.provider, newKeyForm.name, newKeyForm.apiKey);
                                    setNewKeyForm({ provider: 'gemini', name: '', apiKey: '' });
                                    const { data } = await apiKeysAPI.list();
                                    setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
                                    checkGeminiKeys();
                                } catch (error) {
                                    alert(error.response?.data?.name?.[0] || error.response?.data?.detail || 'Failed to add API key');
                                }
                            }} className="space-y-5">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="block text-[10px] font-bold text-gray-600 uppercase tracking-tighter px-1">Engine</label>
                                        <select
                                            value={newKeyForm.provider}
                                            onChange={(e) => setNewKeyForm({ ...newKeyForm, provider: e.target.value })}
                                            className="input-field w-full text-xs py-3"
                                            required
                                        >
                                            <option value="gemini" className="bg-[rgb(var(--bg-secondary))]">Google Gemini</option>
                                        </select>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="block text-[10px] font-bold text-gray-600 uppercase tracking-tighter px-1">Name</label>
                                        <input
                                            type="text"
                                            value={newKeyForm.name}
                                            onChange={(e) => setNewKeyForm({ ...newKeyForm, name: e.target.value })}
                                            className="input-field w-full text-xs py-3"
                                            placeholder="e.g. Production Engine"
                                            required
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="block text-[10px] font-bold text-gray-600 uppercase tracking-tighter px-1">API Key</label>
                                    <input
                                        type="password"
                                        value={newKeyForm.apiKey}
                                        onChange={(e) => setNewKeyForm({ ...newKeyForm, apiKey: e.target.value })}
                                        className="input-field w-full text-xs py-3"
                                        placeholder="AIza..."
                                        required
                                    />
                                </div>
                                <button type="submit" className="w-full py-4 rounded-2xl bg-cosmic-cyan/10 hover:bg-cosmic-cyan/20 border border-white/10 transition-all font-bold text-xs uppercase tracking-widest text-cosmic-cyan">
                                    Authorize Secret
                                </button>
                            </form>
                        </div>

                        {/* Existing Keys List */}
                        <div className="space-y-6">
                            <h3 className="text-sm font-bold mb-6 flex items-center gap-2 text-gray-400 uppercase tracking-widest">
                                <svg className="w-4 h-4 text-cosmic-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                </svg> Active Credentials
                            </h3>
                            {!userApiKeys || userApiKeys.length === 0 ? (
                                <div className="text-gray-600 text-center py-16 glass-card !bg-transparent !border-dashed border-white/10 rounded-3xl">
                                    <p className="text-sm italic">No credentials currently authorized.</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-4">
                                    {userApiKeys.map((key) => (
                                        <div key={key.id} className="group flex items-center justify-between p-5 glass-card !bg-white/5 !border-white/5 hover:!border-white/20 transition-all relative overflow-hidden">
                                            <div className="absolute top-0 left-0 w-1 h-full bg-cosmic-cyan opacity-50 group-hover:opacity-100 transition-opacity"></div>
                                            <div>
                                                <div className="font-bold text-sm tracking-tight">{key.name}</div>
                                                <div className="text-[10px] text-gray-500 uppercase flex gap-4 mt-2">
                                                    <span className="text-cosmic-cyan font-bold">{key.provider}</span>
                                                    <span>Vault ID: ...${key.id.toString().slice(-4)}</span>
                                                    <span>Registered: {new Date(key.created_at).toLocaleDateString()}</span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={async () => {
                                                    if (confirm('Permanently purge this credential from the vault?')) {
                                                        try {
                                                            await apiKeysAPI.delete(key.id);
                                                            const { data } = await apiKeysAPI.list();
                                                            setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
                                                            checkGeminiKeys();
                                                        } catch (error) {
                                                            alert('Failed to delete key');
                                                        }
                                                    }
                                                }}
                                                className="opacity-0 group-hover:opacity-100 p-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/30 text-red-500 transition-all border border-red-500/10"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
