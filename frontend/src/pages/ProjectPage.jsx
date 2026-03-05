import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI } from '../api/client';
import CustomSelect from '../components/CustomSelect';
import DependencyGraph from '../components/DependencyGraph';
import CodePreview from '../components/CodePreview';
import PipelineStepper from '../components/PipelineStepper';

export default function ProjectPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('status');

    // Editing State
    const [isEditing, setIsEditing] = useState(false);
    const [editSpec, setEditSpec] = useState(null);
    const [availableVersions, setAvailableVersions] = useState({});

    const getDuration = () => {
        if (!project?.completed_at) return null;
        const start = new Date(project.created_at);
        const end = new Date(project.completed_at);
        const diff = end - start;
        const minutes = Math.floor(diff / 60000);
        const seconds = ((diff % 60000) / 1000).toFixed(0);
        return `${minutes}m ${seconds}s`;
    };

    useEffect(() => {
        if (project?.intent_spec && !editSpec) {
            setEditSpec(project.intent_spec);
        }
    }, [project?.intent_spec]);

    useEffect(() => {
        const fetchVersions = async () => {
            try {
                const { data } = await projectsAPI.getVersions();
                setAvailableVersions(data);
            } catch (e) {
                console.error('Failed to fetch versions:', e);
            }
        };
        fetchVersions();
    }, []);

    useEffect(() => {
        fetchProject();

        const interval = setInterval(() => {
            if (project && (project.status === 'completed' || project.status === 'failed')) {
                clearInterval(interval);
            } else {
                pollStatus();
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [id, project?.status]);

    const fetchProject = async () => {
        try {
            const { data } = await projectsAPI.get(id);
            setProject(data);
        } catch (error) {
            console.error('Failed to fetch project:', error);
        } finally {
            setLoading(false);
        }
    };

    const pollStatus = async () => {
        try {
            const { data } = await projectsAPI.getStatus(id);
            setProject((prev) => ({ ...prev, ...data }));
            if (data.status === 'completed' || data.status === 'failed') {
                fetchProject();
            }
        } catch (error) {
            console.error('Failed to poll status:', error);
        }
    };

    const handleDownload = async () => {
        try {
            const { data } = await projectsAPI.download(id);
            const url = window.URL.createObjectURL(new Blob([data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${project.name || `project_${id}`}.zip`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            alert('Failed to download project');
        }
    };

    const handleUpdateSpec = async () => {
        try {
            await projectsAPI.updateSpec(id, editSpec);
            setIsEditing(false);
            fetchProject();
        } catch (error) {
            alert('Failed to update specification: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleConfirmSpec = async () => {
        try {
            await projectsAPI.confirmSpec(id);
            fetchProject();
        } catch (error) {
            alert('Failed to confirm specification: ' + (error.response?.data?.detail || error.message));
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-2xl font-display text-[rgb(var(--color-primary))] animate-pulse">Loading project...</div>
            </div>
        );
    }

    if (!project) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-xl">Project not found</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-4">
            {/* Header */}
            <div className="glass-card p-6 mb-6 border-b border-[rgb(var(--color-brand-separator)/0.3)]">
                <div className="flex justify-between items-start">
                    <div>
                        <button onClick={() => navigate('/dashboard')} className="text-[rgb(var(--color-primary))] transition-transform hover:scale-110 mb-4 inline-block font-bold">
                            ← Back to Dashboard
                        </button>
                        <h1 className="text-3xl font-bold mb-2">{project.name || `Project #${project.id}`}</h1>
                        <p className="text-[rgb(var(--text-secondary))] mb-4">{project.prompt}</p>

                        <div className="flex flex-wrap gap-3">
                            <div className="px-3 py-1 bg-[rgb(var(--bg-secondary)/0.5)] border border-[rgb(var(--border-primary))] rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-widest">Model</span>
                                <span className="text-xs font-bold text-[rgb(var(--color-primary))] uppercase">{project.gemini_model?.replace('gemini-', '')}</span>
                            </div>
                            <div className="px-3 py-1 bg-[rgb(var(--bg-secondary)/0.5)] border border-[rgb(var(--border-primary))] rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-widest">API Key</span>
                                <span className="text-xs font-bold text-[rgb(var(--color-primary))] uppercase">{project.api_key_name}</span>
                            </div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className={`inline-block px-4 py-2 rounded-full mb-2 ${project.status === 'completed' ? 'bg-[rgb(var(--status-success)/0.2)] text-[rgb(var(--status-success))]' :
                            project.status === 'failed' ? 'bg-[rgb(var(--status-error)/0.2)] text-[rgb(var(--status-error))]' :
                                'bg-[rgb(var(--status-info)/0.2)] text-[rgb(var(--status-info))] animate-pulse'
                            }`}>
                            {project.status === 'failed' && project.error_message?.includes('Cancelled') ? 'cancelled' : project.status}
                        </div>
                        {project.status !== 'completed' && project.status !== 'failed' && (
                            <button
                                onClick={async () => {
                                    if (confirm('Terminate this project generation?')) {
                                        try {
                                            await projectsAPI.cancel(id);
                                            fetchProject();
                                        } catch (error) {
                                            alert('Failed to terminate: ' + (error.response?.data?.detail || error.message));
                                        }
                                    }
                                }}
                                className="block w-full mt-2 px-4 py-2 rounded-lg bg-[rgb(var(--status-warning)/0.1)] transition-transform hover:scale-105 text-[rgb(var(--status-warning))] border border-[rgb(var(--status-warning)/0.3)] text-sm font-bold flex items-center justify-center gap-2"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    <rect x="9" y="9" width="6" height="6" strokeWidth="2" />
                                </svg> Terminate Build
                            </button>
                        )}
                        {project.status === 'completed' && (
                            <button onClick={handleDownload} className="neon-button block w-full mt-2 flex items-center justify-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg> Download ZIP
                            </button>
                        )}
                        {(project.status === 'failed' || (project.status === 'failed' && project.error_message?.includes('Cancelled'))) && (
                            <button
                                onClick={() => {
                                    navigate('/dashboard', {
                                        state: { retryProject: project }
                                    });
                                }}
                                className="block w-full mt-2 px-4 py-2 rounded-lg bg-[rgb(var(--bg-primary))] transition-transform hover:scale-105 text-[rgb(var(--color-primary))] border border-[rgb(var(--color-primary))] text-sm font-bold flex items-center justify-center gap-2"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg> Retry Generation
                            </button>
                        )}
                    </div>
                </div>

                {project.status !== 'failed' && <PipelineStepper status={project.status} />}
            </div>

            {/* Tabs Navigation */}
            <div className="bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-primary))] rounded-3xl mb-6 overflow-hidden">
                <div className="flex">
                    {['status', 'intent-spec', 'components', 'code'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-6 py-4 font-bold transition-all ${activeTab === tab
                                ? 'bg-[rgb(var(--bg-primary))] text-[rgb(var(--color-primary))] border-b-2 border-[rgb(var(--color-primary))]'
                                : 'text-[rgb(var(--text-secondary))] hover:text-[rgb(var(--text-primary))]'
                                }`}
                        >
                            {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div className="glass-card p-6 min-h-[60vh]">
                {/* Status Tab */}
                {activeTab === 'status' && (
                    <div className="space-y-6 animate-fade-in">
                        {project.status === 'review_required' && (
                            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-6 mb-8">
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 shrink-0">
                                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                        </svg>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold text-yellow-500 mb-1">Review Specification Required</h3>
                                        <p className="text-yellow-200/70 mb-4 max-w-2xl text-sm italic">
                                            "{project.intent_spec?.explanation || "The intent prompt was vague. The system has made some intelligent assumptions to move forward."}"
                                        </p>
                                        <div className="flex gap-3">
                                            <button onClick={handleConfirmSpec} className="px-6 py-2 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 transition-colors shadow-lg shadow-yellow-500/20">
                                                Confirm & Generate
                                            </button>
                                            <button onClick={() => { setActiveTab('intent-spec'); setIsEditing(true); }} className="px-6 py-2 bg-white/5 text-white font-bold rounded-lg hover:bg-white/10 transition-colors border border-white/10">
                                                Edit Spec
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4 p-6 bg-white/5 rounded-2xl border border-white/5">
                                <h3 className="text-xs font-bold text-[rgb(var(--text-secondary))] uppercase tracking-widest">Build Status</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Status</span><span className="badge-info capitalize">{project.status}</span></div>
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Current Stage</span><span className="text-sm font-bold">{project.current_stage || 'N/A'}</span></div>
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Progress</span><span className="text-sm font-black text-[rgb(var(--color-primary))]">{project.progress}%</span></div>
                                </div>
                            </div>
                            <div className="space-y-4 p-6 bg-white/5 rounded-2xl border border-white/5">
                                <h3 className="text-xs font-bold text-[rgb(var(--text-secondary))] uppercase tracking-widest">Environment</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Model</span><span className="text-xs font-bold uppercase">{project.gemini_model}</span></div>
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Duration</span><span className="text-xs font-bold text-[rgb(var(--color-primary))]">{getDuration() || 'In Progress'}</span></div>
                                    <div className="flex justify-between items-center"><span className="text-sm opacity-60">Created At</span><span className="text-xs font-bold">{new Date(project.created_at).toLocaleString()}</span></div>
                                </div>
                            </div>
                        </div>

                        {project.error_message && (
                            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm font-medium">
                                <span className="font-bold mr-2 uppercase text-[10px] bg-red-400 text-black px-1.5 py-0.5 rounded">Error</span>
                                {project.error_message}
                            </div>
                        )}
                    </div>
                )}

                {/* Intent Spec Tab */}
                {activeTab === 'intent-spec' && (
                    <div className="animate-fade-in space-y-6">
                        <div className="flex justify-between items-center">
                            <h2 className="text-2xl font-bold">Intent Specification</h2>
                            <div className="flex gap-3">
                                {isEditing && (
                                    <button onClick={handleUpdateSpec} className="px-4 py-2 bg-[rgb(var(--color-primary))] text-black font-bold rounded-lg hover:opacity-90">
                                        Save Changes
                                    </button>
                                )}
                                <button
                                    onClick={() => setIsEditing(!isEditing)}
                                    className={`px-4 py-2 font-bold rounded-lg border transition-all ${isEditing ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-white/5 border-white/10 text-white'}`}
                                >
                                    {isEditing ? 'Cancel Edit' : 'Edit Spec'}
                                </button>
                            </div>
                        </div>

                        {!project.intent_spec && !isEditing ? (
                            <div className="flex flex-col items-center justify-center py-20 opacity-30">
                                <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                <p>Specification not yet generated</p>
                            </div>
                        ) : isEditing ? (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                <div className="space-y-6">
                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                                        <h3 className="text-lg font-bold mb-6 text-[rgb(var(--color-primary))]">Technology Stack</h3>
                                        <div className="space-y-4">
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <CustomSelect
                                                    label="Backend"
                                                    options={[{ value: 'none', label: 'None' }, { value: 'fastapi', label: 'FastAPI' }, { value: 'django', label: 'Django' }, { value: 'express', label: 'Express' }, { value: 'springboot', label: 'Spring Boot' }]}
                                                    value={editSpec?.stack?.backend || 'none'}
                                                    onChange={v => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, backend: v === 'none' ? null : v }, backend_version: null })}
                                                />
                                                {editSpec?.stack?.backend && availableVersions[editSpec.stack.backend] && (
                                                    <CustomSelect
                                                        label={`${editSpec.stack.backend} Version`}
                                                        options={availableVersions[editSpec.stack.backend].map(v => ({ value: v, label: v }))}
                                                        value={editSpec?.backend_version || ''}
                                                        placeholder="Auto (Latest)"
                                                        onChange={v => setEditSpec({ ...editSpec, backend_version: v })}
                                                    />
                                                )}
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <CustomSelect
                                                    label="Frontend"
                                                    options={[{ value: 'none', label: 'None' }, { value: 'react', label: 'React' }, { value: 'vue', label: 'Vue' }, { value: 'nextjs', label: 'Next.js' }]}
                                                    value={editSpec?.stack?.frontend || 'none'}
                                                    onChange={v => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, frontend: v === 'none' ? null : v }, frontend_version: null })}
                                                />
                                                {editSpec?.stack?.frontend && availableVersions[editSpec.stack.frontend] && (
                                                    <CustomSelect
                                                        label={`${editSpec.stack.frontend} Version`}
                                                        options={availableVersions[editSpec.stack.frontend].map(v => ({ value: v, label: v }))}
                                                        value={editSpec?.frontend_version || ''}
                                                        placeholder="Auto (Latest)"
                                                        onChange={v => setEditSpec({ ...editSpec, frontend_version: v })}
                                                    />
                                                )}
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <CustomSelect
                                                    label="Database"
                                                    options={[{ value: 'none', label: 'None' }, { value: 'sqlite', label: 'SQLite' }, { value: 'postgres', label: 'PostgreSQL' }, { value: 'mongodb', label: 'MongoDB' }]}
                                                    value={editSpec?.stack?.database || 'none'}
                                                    onChange={v => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, database: v === 'none' ? null : v } })}
                                                />
                                                {editSpec?.stack?.database && availableVersions[editSpec.stack.database] && (
                                                    <CustomSelect
                                                        label={`${editSpec.stack.database} Version`}
                                                        options={availableVersions[editSpec.stack.database].map(v => ({ value: v, label: v }))}
                                                        value={editSpec?.database_version || ''}
                                                        placeholder="Auto (Default)"
                                                        onChange={v => setEditSpec({ ...editSpec, database_version: v })}
                                                    />
                                                )}
                                            </div>

                                            <div className="pt-6 border-t border-white/5 grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <CustomSelect
                                                    label="API Type"
                                                    options={[{ value: 'rest', label: 'REST API' }, { value: 'graphql', label: 'GraphQL' }, { value: 'none', label: 'None' }]}
                                                    value={editSpec?.api_type || 'rest'}
                                                    onChange={v => setEditSpec({ ...editSpec, api_type: v })}
                                                />
                                                <CustomSelect
                                                    label="Complexity"
                                                    options={[{ value: 'minimal', label: 'Minimal (Basic MVP)' }, { value: 'standard', label: 'Standard (Production)' }, { value: 'full', label: 'Full (Enterprise)' }]}
                                                    value={editSpec?.complexity || 'minimal'}
                                                    onChange={v => setEditSpec({ ...editSpec, complexity: v })}
                                                />
                                            </div>
                                            <CustomSelect
                                                label="Auth Method"
                                                options={[{ value: 'none', label: 'None' }, { value: 'jwt', label: 'JWT' }, { value: 'session', label: 'Session' }]}
                                                value={editSpec?.constraints?.auth_method || 'none'}
                                                onChange={v => setEditSpec({ ...editSpec, constraints: { ...editSpec.constraints, auth_method: v === 'none' ? null : v } })}
                                            />
                                        </div>
                                    </div>
                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/10 text-sm">
                                        <h3 className="text-lg font-bold mb-4">Features</h3>
                                        <div className="flex flex-wrap gap-2 mb-4">
                                            {['authentication', 'user_profiles', 'file_upload', 'notifications', 'search', 'admin_panel'].map(f => (
                                                <button
                                                    key={f}
                                                    onClick={() => {
                                                        const features = editSpec.features.includes(f) ? editSpec.features.filter(x => x !== f) : [...editSpec.features, f];
                                                        setEditSpec({ ...editSpec, features });
                                                    }}
                                                    className={`px-3 py-1 rounded-full border text-[10px] font-bold uppercase transition-all ${editSpec.features.includes(f) ? 'bg-[rgb(var(--color-primary))]/20 border-[rgb(var(--color-primary))] text-[rgb(var(--color-primary))]' : 'bg-white/5 border-white/10 text-white/30'}`}
                                                >
                                                    {f.replace('_', ' ')}
                                                </button>
                                            ))}
                                        </div>
                                        <div className="pt-4 border-t border-white/5">
                                            <div className="text-[10px] font-bold text-white/20 uppercase mb-3 tracking-widest">Custom Features</div>
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                {editSpec?.features?.filter(f => !['authentication', 'user_profiles', 'file_upload', 'notifications', 'search', 'admin_panel'].includes(f)).map((f, i) => (
                                                    <span key={i} className="px-3 py-1 bg-[rgb(var(--color-primary))]/10 border border-[rgb(var(--color-primary))/0.3] rounded-full text-[10px] uppercase font-bold text-[rgb(var(--text-primary))] flex items-center gap-2">
                                                        {f}
                                                        <button onClick={() => setEditSpec({ ...editSpec, features: editSpec.features.filter(x => x !== f) })} className="text-red-500 hover:text-red-400">×</button>
                                                    </span>
                                                ))}
                                            </div>
                                            <div className="flex gap-2">
                                                <input
                                                    type="text"
                                                    placeholder="Add custom feature..."
                                                    id="customFeatureInput"
                                                    className="flex-1 bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:outline-none focus:border-[rgb(var(--color-primary))]"
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter' && e.target.value.trim()) {
                                                            const val = e.target.value.trim().toLowerCase().replace(' ', '_');
                                                            if (!editSpec.features.includes(val)) {
                                                                setEditSpec({ ...editSpec, features: [...editSpec.features, val] });
                                                            }
                                                            e.target.value = '';
                                                        }
                                                    }}
                                                />
                                                <button
                                                    onClick={() => {
                                                        const input = document.getElementById('customFeatureInput');
                                                        if (input.value.trim()) {
                                                            const val = input.value.trim().toLowerCase().replace(' ', '_');
                                                            if (!editSpec.features.includes(val)) {
                                                                setEditSpec({ ...editSpec, features: [...editSpec.features, val] });
                                                            }
                                                            input.value = '';
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-xl font-bold transition-all"
                                                >
                                                    +
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="p-6 bg-white/5 rounded-2xl border border-white/10 overflow-y-auto max-h-[700px]">
                                    <h3 className="text-lg font-bold mb-6">Data Entities</h3>
                                    <div className="space-y-4">
                                        {editSpec?.data_entities?.map((entity, idx) => (
                                            <div key={idx} className="p-4 bg-black/20 rounded-xl border border-white/5 relative group">
                                                <button onClick={() => setEditSpec({ ...editSpec, data_entities: editSpec.data_entities.filter((_, i) => i !== idx) })} className="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">×</button>
                                                <input
                                                    type="text"
                                                    value={entity.name}
                                                    onChange={e => {
                                                        const next = [...editSpec.data_entities];
                                                        next[idx].name = e.target.value;
                                                        setEditSpec({ ...editSpec, data_entities: next });
                                                    }}
                                                    className="bg-transparent text-[rgb(var(--color-primary))] font-bold border-b border-white/10 mb-2 focus:outline-none"
                                                />
                                                <div className="flex flex-wrap gap-1 mb-2">
                                                    {entity.fields.map((f, fi) => (
                                                        <span key={fi} className="inline-flex items-center gap-1 px-2 py-0.5 bg-white/5 text-[10px] font-bold rounded-lg">
                                                            {f}
                                                            <button onClick={() => {
                                                                const next = [...editSpec.data_entities];
                                                                next[idx].fields = entity.fields.filter((_, i) => i !== fi);
                                                                setEditSpec({ ...editSpec, data_entities: next });
                                                            }} className="text-red-500 hover:text-red-400">×</button>
                                                        </span>
                                                    ))}
                                                </div>
                                                <input
                                                    type="text"
                                                    placeholder="Add field..."
                                                    className="w-full bg-white/5 border border-white/5 rounded-lg p-2 text-xs focus:outline-none focus:border-[rgb(var(--color-primary))]"
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter' && e.target.value.trim()) {
                                                            const next = [...editSpec.data_entities];
                                                            next[idx].fields = [...entity.fields, e.target.value.trim()];
                                                            setEditSpec({ ...editSpec, data_entities: next });
                                                            e.target.value = '';
                                                        }
                                                    }}
                                                />
                                            </div>
                                        ))}
                                        <button onClick={() => setEditSpec({ ...editSpec, data_entities: [...editSpec.data_entities, { name: 'NewEntity', fields: ['id'] }] })} className="w-full py-2 border border-dashed border-white/20 rounded-xl text-xs font-bold opacity-50 hover:opacity-100">+ Add Entity</button>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-8">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/5">
                                        <div className="badge-gold mb-6 uppercase tracking-[0.2em] text-[10px]">Architecture Stack</div>
                                        <div className="space-y-4">
                                            <div className="flex justify-between items-center"><span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">Backend</span><span className="text-sm font-bold text-[rgb(var(--color-primary))]">{project.intent_spec.stack.backend || 'None'} {project.intent_spec.backend_version && `(v${project.intent_spec.backend_version})`}</span></div>
                                            <div className="flex justify-between items-center"><span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">Frontend</span><span className="text-sm font-bold text-[rgb(var(--color-primary))]">{project.intent_spec.stack.frontend || 'None'} {project.intent_spec.frontend_version && `(v${project.intent_spec.frontend_version})`}</span></div>
                                            <div className="flex justify-between items-center"><span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">Database</span><span className="text-sm font-bold">{project.intent_spec.stack.database || 'None'} {project.intent_spec.database_version && `(v${project.intent_spec.database_version})`}</span></div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">API Type</span>
                                                <span className="text-sm font-bold uppercase text-[rgb(var(--color-primary))]">{project.intent_spec.api_type || 'REST'}</span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">Complexity</span>
                                                <span className={`text-sm font-black capitalize ${project.intent_spec.complexity === 'full' ? 'text-purple-400' : project.intent_spec.complexity === 'standard' ? 'text-blue-400' : 'text-gray-400'}`}>
                                                    {project.intent_spec.complexity}
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm opacity-50 font-bold uppercase tracking-widest text-[10px]">Auth</span>
                                                <span className="text-sm font-black uppercase text-[rgb(var(--text-primary))]">
                                                    {project.intent_spec.constraints?.auth_method || 'None'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/5 col-span-1 md:col-span-2 relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                            <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                                        </div>
                                        <div className="flex justify-between items-center mb-6">
                                            <div className="text-[10px] font-bold text-white/40 uppercase tracking-[0.3em]">AI Assumptions & Logic</div>
                                            {project.intent_spec.vague_intent && <span className="text-[9px] bg-red-500/20 text-red-500 border border-red-500/20 px-2 py-0.5 rounded font-black uppercase">Vague Intent Detected</span>}
                                        </div>
                                        <div className="text-sm leading-relaxed text-white/70 italic border-l-2 border-[rgb(var(--color-primary))]/30 pl-4 py-1">
                                            "{project.intent_spec.explanation || "No specific assumptions recorded."}"
                                        </div>
                                        <div className="mt-8">
                                            <div className="text-[9px] font-bold text-white/20 uppercase mb-3 tracking-widest">Inferred Features</div>
                                            <div className="flex flex-wrap gap-2">
                                                {project.intent_spec.features.map((f, i) => (
                                                    <span key={i} className="px-3 py-1 bg-white/5 border border-white/5 rounded-full text-[10px] uppercase font-black text-white/40 tracking-tighter">
                                                        {f.replace('_', ' ')}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="p-6 bg-white/5 rounded-2xl border border-white/5">
                                    <div className="text-[10px] font-bold text-white/40 uppercase tracking-[0.3em] mb-6">Core Data Models</div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                        {project.intent_spec.data_entities.map((entity, i) => (
                                            <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-[rgb(var(--color-primary))]/20 transition-all">
                                                <div className="font-bold text-sm mb-2 text-[rgb(var(--color-primary))]">{entity.name}</div>
                                                <div className="flex flex-wrap gap-1">
                                                    {entity.fields.slice(0, 5).map((f, fi) => (
                                                        <span key={fi} className="text-[9px] text-white/40">{f}{fi < entity.fields.slice(0, 5).length - 1 ? ',' : ''}</span>
                                                    ))}
                                                    {entity.fields.length > 5 && <span className="text-[9px] text-[rgb(var(--color-primary))] opacity-50">+ {entity.fields.length - 5} more</span>}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Components Tab */}
                {activeTab === 'components' && (
                    <div className="animate-fade-in space-y-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Architecture Graph</h2>
                        </div>
                        {project.component_plan ? (
                            <DependencyGraph components={project.component_plan.components} />
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 opacity-30">
                                <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                                <p>Architecture plan not yet generated</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Code Tab */}
                {activeTab === 'code' && (
                    <div className="animate-fade-in space-y-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold">Generated Source</h2>
                        </div>
                        <CodePreview projectId={id} status={project.status} error={project.error_message} />
                    </div>
                )}
            </div>
        </div>
    );
}
