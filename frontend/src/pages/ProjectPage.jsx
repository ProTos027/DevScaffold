import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI } from '../api/client';

export default function ProjectPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('status');

    useEffect(() => {
        fetchProject();

        // Only poll if project is not in terminal state
        const interval = setInterval(() => {
            if (project && (project.status === 'completed' || project.status === 'failed')) {
                clearInterval(interval);
            } else {
                pollStatus();
            }
        }, 2000); // Poll every 2 seconds for faster updates

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

            // Stop polling if completed or failed
            if (data.status === 'completed' || data.status === 'failed') {
                fetchProject(); // Fetch full project details
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

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-2xl font-display text-cosmic-cyan animate-pulse">Loading project...</div>
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
            <div className="glass-card p-6 mb-6">
                <div className="flex justify-between items-start">
                    <div>
                        <button onClick={() => navigate('/dashboard')} className="text-cosmic-cyan hover:text-cosmic-purple mb-4">
                            ← Back to Dashboard
                        </button>
                        <h1 className="text-3xl font-bold mb-2">{project.name || `Project #${project.id}`}</h1>
                        <p className="text-gray-400">{project.prompt}</p>
                    </div>
                    <div className="text-right">
                        <div className={`inline-block px-4 py-2 rounded-full mb-2 ${project.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                            project.status === 'failed' ? 'bg-red-500/20 text-red-300' :
                                'bg-cosmic-cyan/20 text-cosmic-cyan animate-pulse'
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
                                className="block w-full mt-2 px-4 py-2 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 transition-colors border border-yellow-500/30 text-sm font-bold flex items-center justify-center gap-2"
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
                                className="block w-full mt-2 px-4 py-2 rounded-lg bg-cosmic-cyan/20 hover:bg-cosmic-cyan/30 text-cosmic-cyan transition-colors border border-cosmic-cyan/30 text-sm font-bold flex items-center justify-center gap-2"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg> Retry Generation
                            </button>
                        )}
                    </div>
                </div>

                {/* Pipeline Stepper */}
                {project.status !== 'failed' && (
                    <div className="mt-10 overflow-x-auto pb-4 custom-scrollbar">
                        <div className="flex items-center justify-between min-w-[700px] px-4">
                            {[
                                {
                                    id: 'spec', label: 'Specification',
                                    icon: (
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                        </svg>
                                    ),
                                    stages: ['spec_building', 'validating']
                                },
                                {
                                    id: 'planning', label: 'Architecture',
                                    icon: (
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                                        </svg>
                                    ),
                                    stages: ['planning', 'graph_building']
                                },
                                {
                                    id: 'contract', label: 'Folder Contracts',
                                    icon: (
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                        </svg>
                                    ),
                                    stages: ['folder_contracts']
                                },
                                {
                                    id: 'code', label: 'Implementation',
                                    icon: (
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                        </svg>
                                    ),
                                    stages: ['code_generation']
                                },
                                {
                                    id: 'finish', label: 'Finalization',
                                    icon: (
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                        </svg>
                                    ),
                                    stages: ['assembling', 'completed']
                                }
                            ].map((step, index, array) => {
                                const isCompleted = project.status === 'completed' ||
                                    array.slice(index + 1).some(s => s.stages.includes(project.status));
                                const isActive = step.stages.includes(project.status);
                                const isFuture = !isCompleted && !isActive;

                                return (
                                    <React.Fragment key={step.id}>
                                        <div className="flex flex-col items-center gap-3 relative z-10">
                                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-xl transition-all duration-500 border-2 ${isCompleted ? 'bg-cosmic-cyan/20 border-cosmic-cyan text-cosmic-cyan' :
                                                isActive ? 'bg-cosmic-cyan border-white/20 text-space-900 animate-pulse' :
                                                    'bg-white/5 border-white/10 text-gray-600'
                                                }`}>
                                                {isCompleted ? (
                                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                                                    </svg>
                                                ) : step.icon}
                                            </div>
                                            <div className={`text-xs font-bold uppercase tracking-tighter transition-colors duration-500 whitespace-nowrap ${isCompleted ? 'text-cosmic-cyan' : isActive ? 'text-white' : 'text-gray-600'
                                                }`}>
                                                {step.label}
                                            </div>
                                        </div>
                                        {index < array.length - 1 && (
                                            <div className="flex-1 h-[2px] mx-4 -mt-8 relative overflow-hidden bg-black/10 dark:bg-white/5">
                                                <div
                                                    className="absolute inset-0 bg-cosmic-cyan transition-all duration-1000 origin-left"
                                                    style={{ transform: isCompleted ? 'scaleX(1)' : 'scaleX(0)' }}
                                                />
                                            </div>
                                        )}
                                    </React.Fragment>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* Tabs */}
            <div className="glass-card mb-6">
                <div className="flex border-b border-black/10 dark:border-white/10">
                    {['status', 'intent-spec', 'components'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-6 py-4 font-medium transition-colors ${activeTab === tab
                                ? 'border-b-2 border-cosmic-cyan text-cosmic-cyan'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div className="glass-card p-6">
                {activeTab === 'status' && (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold mb-4">Pipeline Status</h2>

                        {project.error_message && (
                            <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg">
                                <strong>Error:</strong> {project.error_message}
                            </div>
                        )}

                        <div className="space-y-2">
                            <p><strong>Status:</strong> {project.status}</p>
                            <p><strong>Stage:</strong> {project.current_stage}</p>
                            <p><strong>Progress:</strong> {project.progress}%</p>
                            <p><strong>Created:</strong> {new Date(project.created_at).toLocaleString()}</p>
                            {project.completed_at && (
                                <p><strong>Completed:</strong> {new Date(project.completed_at).toLocaleString()}</p>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'intent-spec' && (
                    <div>
                        <h2 className="text-2xl font-bold mb-4">Intent Specification</h2>
                        {project.intent_spec ? (
                            <pre className="bg-black/30 p-4 rounded-lg overflow-auto text-sm">
                                {JSON.stringify(project.intent_spec, null, 2)}
                            </pre>
                        ) : (
                            <p className="text-gray-400">Intent spec not yet generated</p>
                        )}
                    </div>
                )}

                {activeTab === 'components' && (
                    <div>
                        <h2 className="text-2xl font-bold mb-4">Component Plan</h2>
                        {project.component_plan ? (
                            <div className="space-y-4">
                                {project.component_plan.components.map((comp, idx) => (
                                    <div key={idx} className="bg-white/5 p-4 rounded-lg">
                                        <h3 className="font-bold text-lg text-cosmic-cyan">{comp.id}</h3>
                                        <p className="text-sm text-gray-400 mb-2">{comp.type}</p>
                                        <div className="text-sm">
                                            <strong>Responsibilities:</strong>
                                            <ul className="list-disc list-inside ml-4">
                                                {comp.responsibilities.map((r, i) => (
                                                    <li key={i}>{r}</li>
                                                ))}
                                            </ul>
                                        </div>
                                        {comp.depends_on.length > 0 && (
                                            <p className="text-sm mt-2">
                                                <strong>Depends on:</strong> {comp.depends_on.join(', ')}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-400">Component plan not yet generated</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
