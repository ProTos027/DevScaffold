import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, authAPI, apiKeysAPI } from '../api/client';
import { useTheme } from '../context/ThemeContext';

export default function DashboardPage() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showNewProjectModal, setShowNewProjectModal] = useState(false);
    const [showAPIKeysModal, setShowAPIKeysModal] = useState(false);
    const [prompt, setPrompt] = useState('');
    const [projectName, setProjectName] = useState('');
    const [geminiModel, setGeminiModel] = useState('gemini-1.5-flash');
    const [geminiApiKeyId, setGeminiApiKeyId] = useState(''); // Selected API key ID
    const [geminiKeys, setGeminiKeys] = useState([]); // Available Gemini keys
    const [hasKeys, setHasKeys] = useState({ gemini: false });
    // The original `apiKeys` state for openai/anthropic is removed as per the instruction's implied change.

    // New API Keys Management State
    const [userApiKeys, setUserApiKeys] = useState([]);
    const [newKeyForm, setNewKeyForm] = useState({ provider: 'gemini', name: '', apiKey: '' });

    const { user, logout } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const navigate = useNavigate();

    useEffect(() => {
        fetchProjects();
        checkAPIKeys();
        checkGeminiKeys();
    }, []);

    const checkGeminiKeys = async () => {
        try {
            const { data } = await apiKeysAPI.list();
            const keys = Array.isArray(data) ? data : (data?.results || []);
            const geminiKeys = keys.filter(k => k.provider === 'gemini');

            setGeminiKeys(geminiKeys);
            setHasKeys(prev => ({ ...prev, gemini: geminiKeys.length > 0 }));

            // Auto-select first key if available
            if (geminiKeys.length > 0 && !geminiApiKeyId) {
                setGeminiApiKeyId(geminiKeys[0].id);
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

    const checkAPIKeys = async () => {
        try {
            const { data } = await authAPI.checkKeys();
            setHasKeys(data);
        } catch (error) {
            console.error('Failed to check API keys:', error);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();

        // Check if user has any Gemini API keys
        if (!hasKeys.gemini) {
            alert('Please configure at least one Google Gemini API key first');
            // Load keys and show modal
            setShowAPIKeysModal(true);
            setShowNewProjectModal(false);
            try {
                const { data } = await apiKeysAPI.list();
                setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
            } catch (error) {
                console.error('Failed to load API keys');
                setUserApiKeys([]);
            }
            return;
        }



        try {
            const response = await projectsAPI.create(prompt, geminiModel, projectName, geminiApiKeyId);
            console.log('Project creation response:', response);

            if (response && response.data) {
                console.log('Project created successfully:', response.data);

                // Navigate to project page
                navigate(`/project/${response.data.id}`);
            } else {
                console.error('Unexpected response format:', response);
                alert('Project creation returned unexpected response format');
            }
        } catch (error) {
            console.error('Project creation error:', error);
            alert('Failed to create project: ' + (error.response?.data?.detail || error.response?.data?.gemini_model?.[0] || error.message));
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateAPIKeys = async (e) => {
        e.preventDefault();
        try {
            await authAPI.updateAPIKeys(apiKeys.openai, apiKeys.anthropic);
            alert('API keys updated successfully');
            setShowAPIKeysModal(false);
            await checkAPIKeys();
        } catch (error) {
            alert('Failed to update API keys');
        }
    };

    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="glass-card m-4 p-4">
                <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-display font-bold bg-gradient-to-r from-cosmic-cyan to-cosmic-purple bg-clip-text text-transparent">
                        DevScaffold
                    </h1>
                    <div className="flex items-center gap-4">
                        <span className="text-sm">Welcome, {user?.firstName && user?.lastName ? `${user.firstName} ${user.lastName}` : (user?.firstName || user?.email)}</span>
                        <button onClick={toggleTheme} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                            {isDark ? '☀️' : '🌙'}
                        </button>
                        <button onClick={async () => {
                            setShowAPIKeysModal(true);
                            try {
                                const { data } = await apiKeysAPI.list();
                                // Ensure we always set an array
                                setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
                            } catch (error) {
                                console.error('Failed to load API keys');
                                setUserApiKeys([]); // Set empty array on error
                            }
                        }} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                            🔑 API Keys
                        </button>
                        <button onClick={logout} className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors">
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="p-4">
                <div className="mb-6 flex justify-between items-center">
                    <h2 className="text-2xl font-bold">Your Projects</h2>
                    <button
                        onClick={() => setShowNewProjectModal(true)}
                        className="neon-button"
                    >
                        + New Project
                    </button>
                </div>

                {/* Projects Grid */}
                {loading ? (
                    <div className="text-center text-cosmic-cyan animate-pulse">Loading projects...</div>
                ) : projects.length === 0 ? (
                    <div className="glass-card p-12 text-center">
                        <p className="text-xl text-gray-500">No projects yet. Create your first one!</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {projects.map((project) => (
                            <div
                                key={project.id}
                                className="glass-card p-6 hover:scale-105 transition-all duration-300 relative"
                            >
                                <div
                                    onClick={() => navigate(`/project/${project.id}`)}
                                    className="cursor-pointer"
                                >
                                    <h3 className="font-bold text-lg mb-2">{project.name || `Project #${project.id}`}</h3>
                                    <p className="text-sm text-gray-400 mb-4 line-clamp-2">{project.prompt}</p>
                                    <div className="flex justify-between items-center text-sm">
                                        <span className={`px-3 py-1 rounded-full ${project.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                                            project.status === 'failed' ? 'bg-red-500/20 text-red-300' :
                                                'bg-cosmic-cyan/20 text-cosmic-cyan'
                                            }`}>
                                            {project.status}
                                        </span>
                                        <span className="text-gray-500">{project.progress}%</span>
                                    </div>
                                </div>
                                <button
                                    onClick={async (e) => {
                                        e.stopPropagation();
                                        if (confirm(`Delete project "${project.name || `Project #${project.id}`}"?`)) {
                                            try {
                                                await projectsAPI.delete(project.id);
                                                setProjects(projects.filter(p => p.id !== project.id));
                                            } catch (error) {
                                                alert('Failed to delete project: ' + (error.response?.data?.detail || error.message));
                                            }
                                        }
                                    }}
                                    className="absolute top-4 right-4 p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors"
                                    title="Delete project"
                                >
                                    🗑️
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* New Project Modal */}
            {showNewProjectModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div className="glass-card p-8 max-w-2xl w-full">
                        <h2 className="text-2xl font-bold mb-6">Create New Project</h2>
                        <form onSubmit={handleCreateProject} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Project Name (optional)</label>
                                <input
                                    type="text"
                                    value={projectName}
                                    onChange={(e) => setProjectName(e.target.value)}
                                    className="input-field w-full"
                                    placeholder="My Awesome Project"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Describe your project</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="input-field w-full h-32"
                                    placeholder="Build a minimal React + Django app with JWT authentication and user profiles..."
                                    required
                                />
                            </div>
                            {/* API Key Selector */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Gemini API Key</label>
                                {!hasKeys.gemini ? (
                                    <p className="text-sm text-yellow-400 mt-2">
                                        ⚠️ No Gemini API keys configured. Please add one in the API Keys section.
                                    </p>
                                ) : (
                                    <select
                                        value={geminiApiKeyId}
                                        onChange={(e) => setGeminiApiKeyId(e.target.value)}
                                        className="input-field w-full"
                                    >
                                        {geminiKeys.map((key) => (
                                            <option key={key.id} value={key.id}>
                                                {key.name || `Key ending in ...${key.key_preview}`}
                                            </option>
                                        ))}
                                    </select>
                                )}
                            </div>

                            {/* Gemini Model Selector */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Gemini Model</label>
                                <select
                                    value={geminiModel}
                                    onChange={(e) => setGeminiModel(e.target.value)}
                                    className="input-field w-full"
                                >
                                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended - Fast & Cost-Effective)</option>
                                    <option value="gemini-2.5-pro">Gemini 2.5 Pro (Best Quality)</option>
                                    <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash-Lite (Ultra Fast)</option>
                                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                                </select>
                                {!hasKeys.gemini && <p className="text-sm text-yellow-400 mt-2">⚠️ No Gemini API keys configured</p>}
                            </div>
                            <div className="flex gap-4">
                                <button type="submit" className="neon-button flex-1">
                                    Generate Project
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowNewProjectModal(false)}
                                    className="px-6 py-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* API Keys Modal - New Multi-Key Management */}
            {showAPIKeysModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div className="glass-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <h2 className="text-2xl font-bold mb-2">Configure API Keys</h2>
                        <p className="text-sm text-gray-400 mb-6">Currently supporting Google Gemini. OpenAI and Anthropic coming soon.</p>

                        {/* Add New Key Form */}
                        <div className="mb-6 p-4 bg-white/5 rounded-lg">
                            <h3 className="text-lg font-semibold mb-4">Add New Key</h3>
                            <form onSubmit={async (e) => {
                                e.preventDefault();
                                try {
                                    await apiKeysAPI.create(newKeyForm.provider, newKeyForm.name, newKeyForm.apiKey);
                                    setNewKeyForm({ provider: 'gemini', name: '', apiKey: '' });
                                    // Reload keys
                                    const { data } = await apiKeysAPI.list();
                                    setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
                                } catch (error) {
                                    alert(error.response?.data?.name?.[0] || error.response?.data?.detail || 'Failed to add API key');
                                }
                            }} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Provider</label>
                                    <select
                                        value={newKeyForm.provider}
                                        onChange={(e) => setNewKeyForm({ ...newKeyForm, provider: e.target.value })}
                                        className="input-field w-full"
                                        required
                                    >
                                        <option value="gemini">Google Gemini</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Key Name</label>
                                    <input
                                        type="text"
                                        value={newKeyForm.name}
                                        onChange={(e) => setNewKeyForm({ ...newKeyForm, name: e.target.value })}
                                        className="input-field w-full"
                                        placeholder="e.g., My Primary Key"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">API Key</label>
                                    <input
                                        type="password"
                                        value={newKeyForm.apiKey}
                                        onChange={(e) => setNewKeyForm({ ...newKeyForm, apiKey: e.target.value })}
                                        className="input-field w-full"
                                        placeholder="AIza..."
                                        required
                                    />
                                </div>
                                <button type="submit" className="neon-button w-full">
                                    + Add Key
                                </button>
                            </form>
                        </div>

                        {/* Existing Keys List */}
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold mb-4">Your API Keys</h3>
                            {!userApiKeys || userApiKeys.length === 0 ? (
                                <p className="text-gray-500 text-center py-6">No API keys configured yet</p>
                            ) : (
                                <div className="space-y-3">
                                    {userApiKeys.map((key) => (
                                        <div key={key.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                                            <div>
                                                <div className="font-semibold">🔑 {key.provider.charAt(0).toUpperCase() + key.provider.slice(1)} - {key.name}</div>
                                                <div className="text-sm text-gray-400">Added: {new Date(key.created_at).toLocaleDateString()}</div>
                                            </div>
                                            <button
                                                onClick={async () => {
                                                    if (confirm('Delete this API key?')) {
                                                        try {
                                                            await apiKeysAPI.delete(key.id);
                                                            const { data } = await apiKeysAPI.list();
                                                            setUserApiKeys(Array.isArray(data) ? data : (data?.results || []));
                                                        } catch (error) {
                                                            alert('Failed to delete key');
                                                        }
                                                    }
                                                }}
                                                className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 transition-colors"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Close Button */}
                        <button
                            onClick={() => setShowAPIKeysModal(false)}
                            className="px-6 py-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors w-full"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
