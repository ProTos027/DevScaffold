import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, authAPI, apiKeysAPI } from '../api/client';
import CustomSelect from '../components/CustomSelect';

export default function DashboardPage() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAPIKeysModal, setShowAPIKeysModal] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [prompt, setPrompt] = useState('');
    const [projectName, setProjectName] = useState('');
    const [geminiModel, setGeminiModel] = useState('gemini-2.5-flash');
    const [geminiKeys, setGeminiKeys] = useState([]);
    const [hasKeys, setHasKeys] = useState({ gemini: false });

    // New API Keys Management State
    const [userApiKeys, setUserApiKeys] = useState([]);
    const [newKeyForm, setNewKeyForm] = useState({ provider: 'gemini', name: '', apiKey: '' });

    const { user, logout } = useAuth();
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
            const response = await projectsAPI.create(prompt, geminiModel, projectName);
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
                    className="fixed inset-0 bg-black/60 z-40 transition-opacity duration-300"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <div className={`fixed inset-y-0 left-0 w-72 z-50 bg-[rgb(var(--bg-secondary))] !rounded-none !rounded-r-xl border-r border-[rgb(var(--border-primary))] p-8 flex flex-col transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                {/* User Profile Info */}
                <div className="flex items-center gap-4 mb-10 pb-6 border-b border-[rgb(var(--border-primary))]">
                    <div className="w-12 h-12 rounded-full bg-[rgb(var(--bg-primary))] border-2 border-[rgb(var(--color-primary))] flex items-center justify-center text-xl font-bold text-[rgb(var(--color-primary))]">
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
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-xl bg-[rgb(var(--bg-secondary)/0.5)] text-[rgb(var(--color-primary))] font-medium border border-[rgb(var(--border-primary))]"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                        </svg> New Project
                    </button>

                    <button
                        onClick={openAPIKeysModal}
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-[rgb(var(--bg-secondary)/0.5)] transition-colors text-left text-sm"
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
                            <div className="text-meta text-[rgb(var(--text-secondary))] mb-6 px-4 flex justify-between items-center">
                                <span>Past Projects</span>
                                <span className="bg-[rgb(var(--bg-secondary)/0.5)] px-2 py-0.5 rounded text-[10px] opacity-100">{projects.length}</span>
                            </div>
                            <div className="space-y-3">
                                {projects.map(p => (
                                    <div key={p.id} className="group flex items-center justify-between bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-primary))] hover:border-[rgb(var(--color-primary)/0.3)] p-2 rounded-xl transition-all hover:scale-[1.01]">
                                        <div
                                            onClick={() => { setIsSidebarOpen(false); navigate(`/project/${p.id}`); }}
                                            className="flex-1 cursor-pointer flex items-center gap-2 min-w-0"
                                        >
                                            <span className={`w-2.5 h-2.5 rounded-full shrink-0 border border-[rgb(var(--color-primary))] ${p.status === 'completed' ? 'bg-[rgb(var(--status-success))] !border-none' :
                                                p.status === 'failed' ? 'bg-[rgb(var(--status-error))] !border-none' : 'bg-[rgb(var(--bg-primary))] animate-pulse'
                                                }`} title={p.status} />
                                            <div className="font-bold text-xs truncate transition-colors" title={p.name || `Project ${p.id}`}>
                                                {p.name || `P#${p.id}`}
                                            </div>
                                            <span className="text-[9px] text-[rgb(var(--text-secondary))] shrink-0">{p.progress}%</span>
                                        </div>

                                        {/* Inline Actions */}
                                        <div className="flex gap-1 items-center transition-transform hover:scale-110">
                                            {p.status === 'completed' && (
                                                <button
                                                    onClick={(e) => handleDownload(e, p)}
                                                    className="p-1.5 rounded-md bg-[rgb(var(--status-success)/0.1)] hover:bg-[rgb(var(--status-success)/0.2)] text-[rgb(var(--status-success))]"
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
                                                    className="p-1.5 rounded-md bg-[rgb(var(--color-primary)/0.1)] hover:bg-[rgb(var(--color-primary)/0.2)] text-[rgb(var(--color-primary))]"
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
                                                    className="p-1.5 rounded-md bg-[rgb(var(--status-warning)/0.1)] hover:bg-[rgb(var(--status-warning)/0.2)] text-[rgb(var(--status-warning))]"
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
                                    <div className="px-4 py-8 text-center text-xs text-[rgb(var(--text-secondary))] italic">No projects recorded.</div>
                                )}
                            </div>
                        </div>
                    </div>
                </nav>

                {/* Bottom Actions */}
                <div className="pt-6 border-t border-[rgb(var(--border-primary))] space-y-4">
                    <button
                        onClick={logout}
                        className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl bg-[rgb(var(--status-error)/0.1)] hover:bg-[rgb(var(--status-error)/0.2)] text-[rgb(var(--status-error))] transition-colors border border-[rgb(var(--status-error)/0.1)]"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg> Logout
                    </button>
                </div>
            </div>

            {/* Header */}
            <header className="bg-[rgb(var(--bg-secondary))] !rounded-none py-4 px-8 flex justify-between items-center sticky top-0 z-40 w-full border-x-0 border-t-0 border-b border-[rgb(var(--color-brand-separator)/0.3)]">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 transition-transform hover:scale-110 group"
                        aria-label="Toggle Project Navigator"
                    >
                        <svg className="w-6 h-6 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                    <div className="text-3xl font-display font-bold cursor-pointer" onClick={() => navigate('/')}>
                        <span className="text-brand-gradient">DevScaffold</span>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <span className="hidden md:block text-label text-[rgb(var(--text-secondary))] opacity-50">Generator</span>
                    <div className="w-8 h-8 rounded-full bg-cosmic-cyan flex items-center justify-center text-xs font-bold border border-[rgb(var(--border-primary))] text-[rgb(var(--bg-primary))]">
                        {user?.firstName?.[0] || user?.email?.[0]?.toUpperCase()}
                    </div>
                </div>
            </header>

            {/* Main Content Area - Unified Command Center */}
            <main className="p-4 max-w-4xl mx-auto pt-10">
                <div className="bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-primary))] rounded-3xl p-12 animate-fade-in relative">
                    {/* Decorative Background Element - Removed Blur/Glow */}


                    <div className="relative z-10 text-center mb-12">
                        <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">Initialize <span className="text-gold-solid">Pipeline</span></h2>
                        <p className="text-[rgb(var(--text-secondary))] max-w-xl mx-auto">Input prompt below. Our multi-agent system will handle the architectural specification, contract derivation, and production-ready code generation.</p>
                    </div>

                    <form onSubmit={handleCreateProject} className="space-y-10 relative z-10">
                        <div className="space-y-6">
                            <div className="group">
                                <label className="block text-xs font-bold uppercase tracking-widest text-[rgb(var(--text-secondary))] mb-3 px-2">Title</label>
                                <input
                                    type="text"
                                    value={projectName}
                                    onChange={(e) => setProjectName(e.target.value)}
                                    className="input-field w-full text-xl py-5 px-6 !bg-[rgb(var(--bg-secondary)/0.5)] border-[rgb(var(--border-primary))] transition-all font-display"
                                    placeholder="e.g. Banking Platform"
                                    data-gramm="false"
                                    data-quillbot-element="false"
                                    spellCheck="false"
                                />
                            </div>

                            <div className="group">
                                <label className="block text-xs font-bold uppercase tracking-widest text-[rgb(var(--text-secondary))] mb-3 px-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="input-field w-full h-48 resize-none py-5 px-6 !bg-[rgb(var(--bg-secondary)/0.5)] border-[rgb(var(--border-primary))] transition-all leading-relaxed"
                                    placeholder="Describe your vision... (e.g. Build a real estate portal with AI-driven valuation and Mapbox integration)"
                                    required
                                    data-gramm="false"
                                    data-quillbot-element="false"
                                    spellCheck="false"
                                />
                            </div>

                            <div className="group">
                                <label className="block text-xs font-bold uppercase tracking-widest text-[rgb(var(--text-secondary))] mb-3 px-2">Model Selection</label>
                                <CustomSelect
                                    options={[
                                        { value: 'gemini-3-pro-preview', label: 'Gemini 3 Pro' },
                                        { value: 'gemini-3-flash-preview', label: 'Gemini 3 Flash' },
                                        { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
                                        { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
                                        { value: 'gemini-2.5-flash-lite', label: 'Gemini 2.5 Flash-Lite' },
                                    ]}
                                    value={geminiModel}
                                    onChange={setGeminiModel}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="neon-button w-full py-6 text-xl mt-8 font-display font-bold transition-all uppercase tracking-widest flex items-center justify-center gap-4"
                        >
                            <svg className="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg> Generate
                        </button>
                    </form>
                </div>

                <div className="mt-12 text-center text-xs text-[rgb(var(--text-secondary))] uppercase tracking-[0.3em] opacity-30 select-none">
                    100+ projects generated
                </div>
            </main >

            {/* API Keys Modal */}
            {
                showAPIKeysModal && (
                    <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-[70]">
                        <div className="glass-3 p-10 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative animate-fade-in">
                            <div className="flex justify-between items-center mb-2">
                                <h2 className="text-3xl font-display font-bold">Secret <span className="text-gold-solid">Vault</span></h2>
                                <button onClick={() => setShowAPIKeysModal(false)} className="text-[rgb(var(--text-secondary))] hover:text-[rgb(var(--text-primary))] transition-colors">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                            <p className="text-xs font-bold uppercase tracking-widest text-[rgb(var(--text-secondary))] mb-10">Multi-Provider Key Orchestration</p>

                            {/* Add New Key Form */}
                            <div className="mb-10 p-8 bg-[rgb(var(--bg-secondary)/0.3)] rounded-3xl border border-[rgb(var(--border-primary))]">
                                <h3 className="text-sm font-bold mb-6 flex items-center gap-2 text-[rgb(var(--text-secondary))] uppercase tracking-widest">
                                    <svg className="w-4 h-4 text-[rgb(var(--color-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                                        const errorData = error.response?.data;
                                        const errorMessage = errorData
                                            ? (errorData.api_key?.[0] || errorData.name?.[0] || errorData.detail || JSON.stringify(errorData))
                                            : error.message;
                                        alert('Failed to add API key: ' + errorMessage);
                                    }
                                }} className="space-y-5">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <CustomSelect
                                            label="Engine"
                                            options={[{ value: 'gemini', label: 'Google Gemini' }]}
                                            value={newKeyForm.provider}
                                            onChange={(val) => setNewKeyForm({ ...newKeyForm, provider: val })}
                                        />
                                        <div className="space-y-2">
                                            <label className="block text-label text-[rgb(var(--text-secondary))] px-1">Name</label>
                                            <input
                                                type="text"
                                                value={newKeyForm.name}
                                                onChange={(e) => setNewKeyForm({ ...newKeyForm, name: e.target.value })}
                                                className="input-field w-full text-xs py-3"
                                                placeholder="e.g. Production Engine"
                                                required
                                                data-gramm="false"
                                                data-quillbot-element="false"
                                                spellCheck="false"
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="block text-label text-[rgb(var(--text-secondary))] px-1">API Key</label>
                                        <input
                                            type="password"
                                            value={newKeyForm.apiKey}
                                            onChange={(e) => setNewKeyForm({ ...newKeyForm, apiKey: e.target.value })}
                                            className="input-field w-full text-xs py-3"
                                            placeholder="AIza..."
                                            required
                                            data-gramm="false"
                                            data-quillbot-element="false"
                                            spellCheck="false"
                                        />
                                    </div>
                                    <button type="submit" className="w-full py-4 rounded-2xl bg-cosmic-cyan/10 hover:bg-cosmic-cyan/20 border border-[rgb(var(--border-primary))] transition-all font-bold text-xs uppercase tracking-widest text-cosmic-cyan">
                                        Authorize Secret
                                    </button>
                                </form>
                            </div>

                            {/* Existing Keys List */}
                            <div className="space-y-6">
                                <h3 className="text-sm font-bold mb-6 flex items-center gap-2 text-[rgb(var(--text-secondary))] uppercase tracking-widest">
                                    <svg className="w-4 h-4 text-cosmic-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg> Active Credentials
                                </h3>
                                {!userApiKeys || userApiKeys.length === 0 ? (
                                    <div className="text-[rgb(var(--text-secondary))] text-center py-16 glass-card !bg-transparent !border-dashed border-[rgb(var(--border-primary))] rounded-3xl">
                                        <p className="text-sm italic">No credentials currently authorized.</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 gap-4">
                                        {userApiKeys.map((key) => (
                                            <div key={key.id} className="group flex items-center justify-between p-5 glass-card !bg-[rgb(var(--bg-secondary)/0.5)] !border-[rgb(var(--border-primary))] hover:!border-[rgb(var(--border-primary)/0.4)] transition-all relative overflow-hidden">
                                                <div className="absolute top-0 left-0 w-1 h-full bg-cosmic-cyan opacity-50 group-hover:opacity-100 transition-opacity"></div>
                                                <div>
                                                    <div className="font-bold text-sm tracking-tight">{key.name}</div>
                                                    <div className="text-[10px] text-[rgb(var(--text-secondary))] uppercase flex gap-4 mt-2">
                                                        <span className="text-[rgb(var(--color-primary))] font-bold">{key.provider}</span>
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
                )
            }
        </div >
    );
}
