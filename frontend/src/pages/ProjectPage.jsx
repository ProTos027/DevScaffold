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
                            {project.status}
                        </div>
                        {project.status === 'completed' && (
                            <button onClick={handleDownload} className="neon-button block w-full mt-2">
                                📦 Download ZIP
                            </button>
                        )}
                    </div>
                </div>

                {/* Progress Bar */}
                {project.status !== 'completed' && project.status !== 'failed' && (
                    <div className="mt-6">
                        <div className="flex justify-between text-sm mb-2">
                            <span>{project.current_stage}</span>
                            <span>{project.progress}%</span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-cosmic-cyan to-cosmic-purple transition-all duration-500"
                                style={{ width: `${project.progress}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Tabs */}
            <div className="glass-card mb-6">
                <div className="flex border-b border-white/10">
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
