import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import dagre from 'dagre';
import Editor from "@monaco-editor/react";
import 'reactflow/dist/style.css';
import { projectsAPI } from '../api/client';

const DependencyGraph = ({ components }) => {
    const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(() => {
        if (!components || components.length === 0) return { nodes: [], edges: [] };

        const dagreGraph = new dagre.graphlib.Graph();
        dagreGraph.setDefaultEdgeLabel(() => ({}));
        dagreGraph.setGraph({ rankdir: 'TB', ranksep: 80, nodesep: 50 });

        const initialNodes = components.map((comp) => {
            const isData = comp.type === 'data_model';
            const isFrontend = comp.type.includes('frontend') || comp.type.includes('page');
            const isBackend = comp.type.includes('backend') || comp.type.includes('service') || comp.type.includes('controller');

            // Modern, clean colors
            let borderColor = 'rgba(255,255,255,0.1)';
            let textColor = '#fff';
            let bgColor = '#0d0d12'; // Neutral dark grey to match app background
            let glowColor = 'transparent';

            if (isData) {
                borderColor = '#3b82f6'; // Blue
                glowColor = 'rgba(59, 130, 246, 0.1)';
            } else if (isFrontend) {
                borderColor = '#10b981'; // Green/Emerald
                glowColor = 'rgba(16, 185, 129, 0.1)';
            } else if (isBackend) {
                borderColor = '#f59e0b'; // Amber/Gold
                glowColor = 'rgba(245, 158, 11, 0.1)';
            }

            const node = {
                id: comp.id,
                type: 'default',
                data: {
                    label: (
                        <div className="p-1">
                            <div className="text-[7px] uppercase font-black mb-1 opacity-50 tracking-widest" style={{ color: borderColor }}>{comp.type.replace(/_/g, ' ')}</div>
                            <div className="text-[10px] font-bold text-white mb-1 truncate">{comp.id}</div>
                            <div className="text-[7px] text-gray-500 line-clamp-1 leading-tight font-medium">
                                {comp.responsibilities[0]}
                            </div>
                        </div>
                    )
                },
                style: {
                    background: bgColor,
                    border: `1px solid ${borderColor}`,
                    borderRadius: isData ? '6px' : '16px', // Different shapes: Sharper for data, rounded for logic
                    width: 180,
                    padding: '8px',
                    boxShadow: `0 0 15px ${glowColor}`,
                    transition: 'all 0.3s ease'
                }
            };

            dagreGraph.setNode(comp.id, { width: 180, height: 80 });
            return node;
        });

        const initialEdges = [];
        components.forEach((comp) => {
            if (comp.depends_on) {
                const uniqueDeps = Array.from(new Set(comp.depends_on));
                uniqueDeps.forEach((depId) => {
                    initialEdges.push({
                        id: `e-${depId}-${comp.id}`,
                        source: depId,
                        target: comp.id,
                        animated: false,
                        style: { stroke: 'rgba(255,255,255,0.15)', strokeWidth: 1 },
                        markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(255,255,255,0.3)' },
                    });
                    dagreGraph.setEdge(depId, comp.id);
                });
            }
        });

        dagre.layout(dagreGraph);

        const nodes = initialNodes.map((node) => {
            const nodeWithPosition = dagreGraph.node(node.id);
            return {
                ...node,
                position: {
                    x: nodeWithPosition.x - 90,
                    y: nodeWithPosition.y - 40,
                },
            };
        });

        return { nodes, edges: initialEdges };
    }, [components]);

    if (!components || components.length === 0) return null;

    return (
        <div className="space-y-4">
            <div style={{ height: '550px' }} className="w-full bg-space-950/20 rounded-2xl border border-white/5 overflow-hidden relative">
                <div className="absolute top-4 left-4 z-10 p-3 bg-black/40 backdrop-blur-md rounded-xl border border-white/5">
                    <div className="text-[10px] font-bold text-cosmic-cyan uppercase tracking-widest mb-1">Architecture Preview</div>
                    <div className="text-[9px] text-gray-500 uppercase">Interactive Schema</div>
                </div>

                <ReactFlow nodes={layoutedNodes} edges={layoutedEdges} fitView className="bg-transparent">
                    <Controls position="top-right" className="bg-black/50 border-white/10" />
                </ReactFlow>

                <div className="absolute bottom-4 left-4 z-10 flex flex-wrap gap-2">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-lg border border-white/5">
                        <div className="w-2 h-2 rounded-sm border border-[#3b82f6] shadow-[0_0_5px_rgba(59,130,246,0.3)]"></div>
                        <span className="text-[9px] text-gray-400 font-bold uppercase tracking-tighter">Data Model</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-lg border border-white/5">
                        <div className="w-2 h-2 rounded-full border border-[#f59e0b] shadow-[0_0_5px_rgba(245,158,11,0.3)]"></div>
                        <span className="text-[9px] text-gray-400 font-bold uppercase tracking-tighter">Backend</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-lg border border-white/5">
                        <div className="w-2 h-2 rounded-full border border-[#10b981] shadow-[0_0_5px_rgba(16,185,129,0.3)]"></div>
                        <span className="text-[9px] text-gray-400 font-bold uppercase tracking-tighter">Frontend</span>
                    </div>
                </div>

                <div className="absolute bottom-4 right-4 z-10 p-2 px-3 bg-black/40 backdrop-blur-md rounded-lg border border-white/5 flex items-center gap-2">
                    <div className="flex items-center">
                        <div className="w-4 h-[1px] bg-white/40"></div>
                        <div className="w-0 h-0 border-t-[3px] border-t-transparent border-l-[6px] border-l-white/40 border-b-[3px] border-b-transparent -ml-[1px]"></div>
                    </div>
                    <span className="text-[9px] text-gray-400 font-bold uppercase tracking-tighter">Arrow: Depends On</span>
                </div>
            </div>
        </div>
    );
};

const CodePreview = ({ projectId }) => {
    const [fileTree, setFileTree] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContent, setFileContent] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                const { data } = await projectsAPI.browseFiles(projectId);
                setFileTree(data);
                if (data.length > 0) {
                    // Try to find a README.md or the first file to select
                    const findFirstFile = (items) => {
                        for (const item of items) {
                            if (!item.is_dir) return item;
                            if (item.children) {
                                const found = findFirstFile(item.children);
                                if (found) return found;
                            }
                        }
                        return null;
                    };
                    const firstFile = findFirstFile(data);
                    if (firstFile) handleFileSelect(firstFile.path);
                }
            } catch (error) {
                console.error('Failed to fetch files:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchFiles();
    }, [projectId]);

    const handleFileSelect = async (path) => {
        try {
            const { data } = await projectsAPI.readFile(projectId, path);
            setSelectedFile(data);
            setFileContent(data.content);
        } catch (error) {
            console.error('Failed to read file:', error);
        }
    };

    const FileTreeItem = ({ item, depth = 0 }) => {
        const [isOpen, setIsOpen] = useState(true);

        return (
            <div>
                <div
                    className={`flex items-center gap-2 px-2 py-1 cursor-pointer hover:bg-white/5 rounded transition-colors ${selectedFile?.path === item.path ? 'bg-cosmic-cyan/10 text-cosmic-cyan' : 'text-gray-400'}`}
                    style={{ paddingLeft: `${depth * 16 + 8}px` }}
                    onClick={() => item.is_dir ? setIsOpen(!isOpen) : handleFileSelect(item.path)}
                >
                    {item.is_dir ? (
                        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                        </svg>
                    ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                    )}
                    <span className="text-xs truncate">{item.name}</span>
                </div>
                {item.is_dir && isOpen && item.children && (
                    <div>
                        {item.children.map((child, i) => (
                            <FileTreeItem key={i} item={child} depth={depth + 1} />
                        ))}
                    </div>
                )}
            </div>
        );
    };

    if (loading) return <div className="p-8 text-center animate-pulse text-cosmic-cyan">Mapping repository files...</div>;
    if (fileTree.length === 0) return <div className="p-8 text-center text-gray-500">No files found. The build might still be in progress.</div>;

    return (
        <div className="flex h-[600px] bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
            {/* Sidebar */}
            <div className="w-64 border-r border-white/5 bg-black/40 backdrop-blur-md overflow-y-auto p-2 custom-scrollbar">
                <div className="text-[10px] uppercase font-black text-gray-500 mb-4 px-2 tracking-widest">Project Explorer</div>
                {fileTree.map((item, i) => <FileTreeItem key={i} item={item} />)}
            </div>

            {/* Editor Area */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="p-3 border-b border-white/5 bg-black/20 flex items-center justify-between">
                    <div className="flex items-center gap-2 overflow-hidden">
                        <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-gray-500 font-bold uppercase tracking-tighter shrink-0">{selectedFile?.language || 'plain'}</span>
                        <span className="text-xs text-white/70 truncate font-mono">{selectedFile?.path || 'Select a file'}</span>
                    </div>
                </div>
                <div className="flex-1">
                    <Editor
                        height="100%"
                        theme="vs-dark"
                        language={selectedFile?.language || 'plaintext'}
                        value={fileContent || ''}
                        options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            fontSize: 13,
                            fontFamily: "'Fira Code', 'Monaco', monospace",
                            padding: { top: 16 },
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                            backgroundColor: '#00000000'
                        }}
                    />
                </div>
            </div>
        </div>
    );
};

export default function ProjectPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('status');

    // Editing State
    const [isEditing, setIsEditing] = useState(false);
    const [editSpec, setEditSpec] = useState(null);

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
                        <button onClick={() => navigate('/dashboard')} className="text-cosmic-cyan hover:text-cosmic-blue mb-4">
                            ← Back to Dashboard
                        </button>
                        <h1 className="text-3xl font-bold mb-2">{project.name || `Project #${project.id}`}</h1>
                        <p className="text-gray-400 mb-4">{project.prompt}</p>

                        <div className="flex flex-wrap gap-3">
                            <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Model</span>
                                <span className="text-xs font-bold text-cosmic-cyan uppercase">{project.gemini_model?.replace('gemini-', '')}</span>
                            </div>
                            <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">API Key</span>
                                <span className="text-xs font-bold text-cosmic-blue uppercase">{project.api_key_name}</span>
                            </div>
                        </div>
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

            {/* Review Required Banner */}
            {project.status === 'review_required' && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-6 mb-6">
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 shrink-0">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                        <div className="flex-1">
                            <h3 className="text-xl font-bold text-yellow-500 mb-1">Review Specification Required</h3>
                            <p className="text-yellow-200/70 mb-4 max-w-2xl">
                                {project.intent_spec?.explanation || "The intent prompt was vague. The system has made some intelligent assumptions to move forward. Please review and edit the specification below before proceeding with code generation."}
                            </p>
                            <div className="flex gap-3">
                                <button
                                    onClick={handleConfirmSpec}
                                    className="px-6 py-2 bg-yellow-500 text-space-900 font-bold rounded-lg hover:bg-yellow-400 transition-colors"
                                >
                                    Confirm & Generate
                                </button>
                                <button
                                    onClick={() => {
                                        setActiveTab('intent-spec');
                                        setIsEditing(true);
                                    }}
                                    className="px-6 py-2 bg-white/10 text-white font-bold rounded-lg hover:bg-white/20 transition-colors border border-white/10"
                                >
                                    Edit Spec
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="glass-card mb-6">
                <div className="flex border-b border-black/10 dark:border-white/10">
                    {['status', 'intent-spec', 'components', 'code'].map((tab) => (
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

                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white/5 p-6 rounded-2xl border border-white/5">
                                <div className="space-y-3">
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Project Status</span>
                                        <span className="font-bold text-cosmic-cyan uppercase">{project.status}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Current Stage</span>
                                        <span className="text-white font-medium">{project.current_stage || 'N/A'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Build Progress</span>
                                        <span className="text-white font-black">{project.progress}%</span>
                                    </p>
                                </div>
                                <div className="space-y-3">
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">LLM Model</span>
                                        <span className="text-cosmic-cyan font-black uppercase text-[11px]">{project.gemini_model || 'System Default'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">API Key Used</span>
                                        <span className="text-cosmic-blue font-black uppercase text-[11px]">{project.api_key_name || 'N/A'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Started At</span>
                                        <span className="text-gray-300 font-medium text-[11px]">{new Date(project.created_at).toLocaleString()}</span>
                                    </p>
                                    {project.completed_at && (
                                        <p className="flex justify-between items-center text-sm">
                                            <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Finished At</span>
                                            <span className="text-green-400 font-medium text-[11px]">{new Date(project.completed_at).toLocaleString()}</span>
                                        </p>
                                    )}
                                    {project.completed_at && (
                                        <p className="flex justify-between items-center text-sm pt-2 border-t border-white/5">
                                            <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Total Duration</span>
                                            <span className="text-cosmic-cyan font-black text-xs">{getDuration()}</span>
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'intent-spec' && (
                    <div className="space-y-8">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Intent Specification</h2>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setIsEditing(!isEditing)}
                                    className={`px-4 py-2 rounded-lg font-bold transition-all border ${isEditing
                                        ? 'bg-red-500/20 border-red-500/50 text-red-300'
                                        : 'bg-cosmic-cyan/20 border-cosmic-cyan/50 text-cosmic-cyan'
                                        }`}
                                >
                                    {isEditing ? 'Cancel Editing' : 'Edit Specification'}
                                </button>
                                {isEditing && (
                                    <button
                                        onClick={handleUpdateSpec}
                                        className="px-4 py-2 bg-cosmic-cyan text-space-900 font-bold rounded-lg hover:bg-cosmic-cyan/80 transition-all"
                                    >
                                        Save Changes
                                    </button>
                                )}
                            </div>
                        </div>

                        {!project.intent_spec && !isEditing ? (
                            <p className="text-gray-400">Intent spec not yet generated</p>
                        ) : isEditing ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Form Column 1: Stack & Features */}
                                <div className="space-y-6">
                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                            <svg className="w-5 h-5 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                            </svg>
                                            Technology Stack
                                        </h3>
                                        <div className="grid grid-cols-1 gap-4">
                                            <div>
                                                <label className="block text-xs font-bold uppercase text-gray-400 mb-1">Backend</label>
                                                <select
                                                    value={editSpec?.stack?.backend || 'none'}
                                                    onChange={e => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, backend: e.target.value === 'none' ? null : e.target.value } })}
                                                    className="w-full bg-black/50 border border-white/10 rounded-lg p-2 text-white focus:outline-none focus:border-cosmic-cyan"
                                                >
                                                    <option value="none">None/Custom</option>
                                                    <option value="fastapi">FastAPI (Python)</option>
                                                    <option value="django">Django (Python)</option>
                                                    <option value="express">Express (Node.js)</option>
                                                    <option value="springboot">Spring Boot (Java)</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-xs font-bold uppercase text-gray-400 mb-1">Frontend</label>
                                                <select
                                                    value={editSpec?.stack?.frontend || 'none'}
                                                    onChange={e => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, frontend: e.target.value === 'none' ? null : e.target.value } })}
                                                    className="w-full bg-black/50 border border-white/10 rounded-lg p-2 text-white focus:outline-none focus:border-cosmic-cyan"
                                                >
                                                    <option value="none">None/API Only</option>
                                                    <option value="react">React (Vite)</option>
                                                    <option value="vue">Vue (Vite)</option>
                                                    <option value="nextjs">Next.js</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-xs font-bold uppercase text-gray-400 mb-1">Database</label>
                                                <select
                                                    value={editSpec?.stack?.database || 'none'}
                                                    onChange={e => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, database: e.target.value === 'none' ? null : e.target.value } })}
                                                    className="w-full bg-black/50 border border-white/10 rounded-lg p-2 text-white focus:outline-none focus:border-cosmic-cyan"
                                                >
                                                    <option value="none">None</option>
                                                    <option value="sqlite">SQLite</option>
                                                    <option value="postgres">PostgreSQL</option>
                                                    <option value="mongodb">MongoDB</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-6 bg-white/5 rounded-2xl border border-white/10">
                                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                            <svg className="w-5 h-5 text-cosmic-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-7.714 2.143L11 21l-2.286-6.857L1 12l7.714-2.143L11 3z" />
                                            </svg>
                                            System Features
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            {/* Combined list of default and custom features to ensure all are rendered as buttons */}
                                            {Array.from(new Set([...['authentication', 'user_profiles', 'file_upload', 'notifications', 'search', 'admin_panel', 'stripe_payments', 'analytics'], ...editSpec.features])).map(feature => (
                                                <button
                                                    key={feature}
                                                    onClick={() => {
                                                        const features = editSpec.features.includes(feature)
                                                            ? editSpec.features.filter(f => f !== feature)
                                                            : [...editSpec.features, feature];
                                                        setEditSpec({ ...editSpec, features });
                                                    }}
                                                    className={`px-3 py-1 rounded-full text-xs font-bold transition-all border ${editSpec.features.includes(feature)
                                                        ? 'bg-cosmic-blue/20 border-cosmic-blue text-cosmic-blue'
                                                        : 'bg-white/5 border-white/10 text-gray-500'
                                                        }`}
                                                >
                                                    {feature.replace(/_/g, ' ')}
                                                </button>
                                            ))}
                                            <div className="flex gap-2 w-full mt-2">
                                                <input
                                                    type="text"
                                                    placeholder="Add custom feature..."
                                                    className="flex-1 bg-black/50 border border-white/10 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-cosmic-blue"
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter' && e.target.value.trim()) {
                                                            const newFeature = e.target.value.trim().toLowerCase().replace(/\s+/g, '_');
                                                            if (!editSpec.features.includes(newFeature)) {
                                                                setEditSpec({ ...editSpec, features: [...editSpec.features, newFeature] });
                                                            }
                                                            e.target.value = '';
                                                        }
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Form Column 2: Data Entities */}
                                <div className="p-6 bg-white/5 rounded-2xl border border-white/10 h-fit">
                                    <h3 className="text-xl font-bold mb-4 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <svg className="w-5 h-5 text-cosmic-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2 2 2 2 2h12c2 0 2-2 2-2V7c0-2-2-2-2-2H6c-2 0-2 2-2 2zm0 5h16" />
                                            </svg>
                                            Data Entities
                                        </div>
                                        <button
                                            onClick={() => setEditSpec({
                                                ...editSpec,
                                                data_entities: [...editSpec.data_entities, { name: 'NewEntity', fields: ['id', 'name'] }]
                                            })}
                                            className="text-xs bg-cosmic-cyan text-space-900 px-2 py-1 rounded font-bold"
                                        >
                                            + Add Entity
                                        </button>
                                    </h3>
                                    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                                        {editSpec?.data_entities?.map((entity, idx) => (
                                            <div key={idx} className="p-4 bg-black/30 rounded-xl border border-white/5 relative group">
                                                <button
                                                    onClick={() => setEditSpec({
                                                        ...editSpec,
                                                        data_entities: editSpec.data_entities.filter((_, i) => i !== idx)
                                                    })}
                                                    className="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                                <input
                                                    type="text"
                                                    value={entity.name}
                                                    onChange={e => {
                                                        const newEntities = [...editSpec.data_entities];
                                                        newEntities[idx].name = e.target.value;
                                                        setEditSpec({ ...editSpec, data_entities: newEntities });
                                                    }}
                                                    className="bg-transparent text-cosmic-cyan font-bold border-b border-white/10 mb-2 focus:outline-none focus:border-cosmic-cyan"
                                                />
                                                <div className="flex flex-wrap gap-1 mb-3">
                                                    {entity.fields.map((field, fIdx) => (
                                                        <span key={fIdx} className="group/tag inline-flex items-center gap-1 px-2 py-0.5 bg-cosmic-cyan/10 border border-cosmic-cyan/30 text-cosmic-cyan text-[10px] font-bold rounded-full">
                                                            {field}
                                                            <button
                                                                onClick={() => {
                                                                    const newEntities = [...editSpec.data_entities];
                                                                    newEntities[idx].fields = entity.fields.filter((_, i) => i !== fIdx);
                                                                    setEditSpec({ ...editSpec, data_entities: newEntities });
                                                                }}
                                                                className="hover:text-white transition-colors"
                                                            >
                                                                <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" />
                                                                </svg>
                                                            </button>
                                                        </span>
                                                    ))}
                                                </div>
                                                <input
                                                    type="text"
                                                    placeholder="Add field..."
                                                    className="w-full bg-black/20 border border-white/5 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-cosmic-cyan"
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter' && e.target.value.trim()) {
                                                            const newField = e.target.value.trim();
                                                            if (!entity.fields.includes(newField)) {
                                                                const newEntities = [...editSpec.data_entities];
                                                                newEntities[idx].fields = [...entity.fields, newField];
                                                                setEditSpec({ ...editSpec, data_entities: newEntities });
                                                            }
                                                            e.target.value = '';
                                                        }
                                                    }}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {/* Visual Grid Overview */}
                                <div className="p-6 bg-white/5 rounded-2xl border border-white/10 hover:border-cosmic-cyan/30 transition-colors">
                                    <div className="text-xs font-bold text-cosmic-cyan uppercase tracking-widest mb-4">Architecture Stack</div>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-500">Backend</span>
                                            <span className="font-bold text-white">{project.intent_spec.stack.backend || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-500">Frontend</span>
                                            <span className="font-bold text-white">{project.intent_spec.stack.frontend || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-500">Database</span>
                                            <span className="font-bold text-white">{project.intent_spec.stack.database || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-gray-500">Type</span>
                                            <span className="font-bold text-white">{project.intent_spec.project_type}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-6 bg-white/5 rounded-2xl border border-white/10 hover:border-cosmic-blue/30 transition-colors">
                                    <div className="text-xs font-bold text-cosmic-blue uppercase tracking-widest mb-4">Derived Features</div>
                                    <div className="flex flex-wrap gap-2">
                                        {project.intent_spec.features.map((f, i) => (
                                            <span key={i} className="px-3 py-1 bg-cosmic-blue/10 border border-cosmic-blue/30 text-cosmic-blue text-[10px] font-bold uppercase rounded-full">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="p-6 bg-white/5 rounded-2xl border border-white/10 hover:border-white/20 transition-colors">
                                    <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Core Data Models</div>
                                    <div className="space-y-3">
                                        {project.intent_spec.data_entities.slice(0, 4).map((entity, i) => (
                                            <div key={i} className="flex flex-col">
                                                <span className="font-bold text-sm text-white">{entity.name}</span>
                                                <span className="text-[10px] text-gray-500 truncate">{entity.fields.join(', ')}</span>
                                            </div>
                                        ))}
                                        {project.intent_spec.data_entities.length > 4 && (
                                            <div className="text-[10px] text-cosmic-cyan font-bold italic">
                                                + {project.intent_spec.data_entities.length - 4} more entities
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'components' && (
                    <div className="animate-fade-in">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Architecture Graph</h2>
                        </div>
                        {project.component_plan ? (
                            <DependencyGraph components={project.component_plan.components} />
                        ) : (
                            <p className="text-gray-400">Architecture plan not yet generated</p>
                        )}
                    </div>
                )}

                {activeTab === 'code' && (
                    <div className="animate-fade-in">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Generated Source</h2>
                        </div>
                        <CodePreview projectId={id} />
                    </div>
                )}
            </div>
        </div>
    );
}
