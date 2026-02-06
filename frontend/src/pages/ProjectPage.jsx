import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import dagre from 'dagre';
import Editor from "@monaco-editor/react";
import 'reactflow/dist/style.css';
import { projectsAPI } from '../api/client';
import CustomSelect from '../components/CustomSelect';

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
            let borderColor = 'rgb(var(--node-border-default))';
            let textColor = 'rgb(var(--node-text))';
            let bgColor = 'rgb(var(--node-bg))';
            let glowColor = 'transparent';

            if (isData) {
                borderColor = 'rgb(var(--node-data))';
                glowColor = 'rgb(var(--node-data) / 0.1)';
            } else if (isFrontend) {
                borderColor = 'rgb(var(--node-frontend))';
                glowColor = 'rgb(var(--node-frontend) / 0.1)';
            } else if (isBackend) {
                borderColor = 'rgb(var(--node-backend))';
                glowColor = 'rgb(var(--node-backend) / 0.1)';
            }

            const node = {
                id: comp.id,
                type: 'default',
                data: {
                    label: (
                        <div className="p-1">
                            <div className="text-[7px] uppercase font-black mb-1 opacity-50 tracking-widest" style={{ color: borderColor }}>{comp.type.replace(/_/g, ' ')}</div>
                            <div className="text-[10px] font-bold mb-1 truncate" style={{ color: 'rgb(var(--node-text))' }}>{comp.id}</div>
                            <div className="text-[7px] text-[rgb(var(--text-secondary))] line-clamp-1 leading-tight font-medium">
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
                    transition: 'all 0.3s ease',
                    fontFamily: 'var(--font-main)'
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
                        style: { stroke: 'rgb(var(--text-primary) / 0.3)', strokeWidth: 1.5 },
                        markerEnd: { type: MarkerType.ArrowClosed, color: 'rgb(var(--text-primary) / 0.5)' },
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
            <div style={{ height: '550px' }} className="w-full bg-[rgb(var(--bg-secondary))] rounded-2xl border border-[rgb(var(--border-primary))] overflow-hidden relative">
                <div className="absolute top-4 left-4 z-10 p-3 bg-[rgb(var(--bg-primary))] rounded-xl border border-[rgb(var(--border-primary))]">
                    <div className="badge-gold mb-1">Architecture Preview</div>
                    <div className="text-[9px] text-[rgb(var(--text-secondary))] uppercase">Interactive Schema</div>
                </div>

                <ReactFlow nodes={layoutedNodes} edges={layoutedEdges} fitView className="bg-transparent">
                    <Controls position="top-right" className="bg-[rgb(var(--bg-secondary)/0.5)] border-[rgb(var(--border-primary))] !text-[rgb(var(--text-primary))]" />
                </ReactFlow>

                <div className="absolute bottom-4 left-4 z-10 flex flex-wrap gap-2">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-[rgb(var(--bg-primary))] rounded-lg border border-[rgb(var(--border-primary))] transition-transform hover:scale-105">
                        <div className="w-2 h-2 rounded-sm border border-[rgb(var(--node-data))]"></div>
                        <span className="text-[9px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-tighter">Data Model</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-[rgb(var(--bg-secondary)/0.4)] backdrop-blur-md rounded-lg border border-[rgb(var(--border-primary))] transition-transform hover:scale-105">
                        <div className="w-2 h-2 rounded-full border border-[rgb(var(--node-backend))]"></div>
                        <span className="text-[9px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-tighter">Backend</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-[rgb(var(--bg-secondary)/0.4)] backdrop-blur-md rounded-lg border border-[rgb(var(--border-primary))] transition-transform hover:scale-105">
                        <div className="w-2 h-2 rounded-full border border-[rgb(var(--node-frontend))]"></div>
                        <span className="text-[9px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-tighter">Frontend</span>
                    </div>
                </div>

                <div className="absolute bottom-4 right-4 z-10 p-2 px-3 bg-[rgb(var(--bg-secondary)/0.4)] backdrop-blur-md rounded-lg border border-[rgb(var(--border-primary))] flex items-center gap-2">
                    <div className="flex items-center">
                        <div className="w-4 h-[1px] bg-[rgb(var(--text-primary)/0.4)]"></div>
                        <div className="w-0 h-0 border-t-[3px] border-t-transparent border-l-[6px] border-l-[rgb(var(--text-primary)/0.4)] border-b-[3px] border-b-transparent -ml-[1px]"></div>
                    </div>
                    <span className="text-[9px] text-[rgb(var(--text-secondary))] font-bold uppercase tracking-tighter">Arrow: Depends On</span>
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
                    className={`flex items-center gap-2 px-2 py-1 cursor-pointer transition-transform hover:scale-[1.02] rounded ${selectedFile?.path === item.path ? 'bg-[rgb(var(--code-selected))] text-cosmic-cyan' : 'text-[rgb(var(--text-secondary))]'}`}
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

    if (loading) return <div className="p-8 text-center animate-pulse text-[rgb(var(--color-primary))]">Mapping repository files...</div>;
    if (fileTree.length === 0) return <div className="p-8 text-center text-[rgb(var(--text-secondary))]">No files found. The build might still be in progress.</div>;

    return (
        <div className="flex h-[600px] bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))] overflow-hidden">
            {/* Sidebar */}
            <div className="w-64 border-r border-[rgb(var(--code-sidebar-border))] bg-[rgb(var(--code-sidebar-bg))] backdrop-blur-md overflow-y-auto p-2 custom-scrollbar">
                <div className="text-[10px] uppercase font-black text-[rgb(var(--text-secondary))] mb-4 px-2 tracking-widest">Project Explorer</div>
                {fileTree.map((item, i) => <FileTreeItem key={i} item={item} />)}
            </div>

            {/* Editor Area */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="p-3 border-b border-[rgb(var(--code-sidebar-border))] bg-[rgb(var(--bg-secondary)/0.3)] flex items-center justify-between">
                    <div className="flex items-center gap-2 overflow-hidden">
                        <span className="text-[10px] bg-[rgb(var(--bg-secondary)/0.5)] border border-[rgb(var(--border-primary)/0.5)] px-2 py-0.5 rounded text-[rgb(var(--text-secondary))] font-bold uppercase tracking-tighter shrink-0">{selectedFile?.language || 'plain'}</span>
                        <span className="text-xs text-[rgb(var(--text-primary)/0.7)] truncate font-mono">{selectedFile?.path || 'Select a file'}</span>
                    </div>
                </div>
                <div className="flex-1">
                    <Editor
                        height="100%"
                        theme={document.documentElement.classList.contains('dark') ? 'vs-dark' : 'vs-light'}
                        language={selectedFile?.language || 'plaintext'}
                        value={fileContent || ''}
                        options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            fontSize: 13,
                            fontFamily: "var(--font-main)",
                            padding: { top: 16 },
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                            backgroundColor: 'transparent'
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
                        <p className="text-gray-400 mb-4">{project.prompt}</p>

                        <div className="flex flex-wrap gap-3">
                            <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Model</span>
                                <span className="text-xs font-bold text-[rgb(var(--color-primary))] uppercase">{project.gemini_model?.replace('gemini-', '')}</span>
                            </div>
                            <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-lg flex items-center gap-2">
                                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">API Key</span>
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
                                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-xl transition-all duration-500 border-2 ${isCompleted ? 'bg-[rgb(var(--bg-primary))] border-[rgb(var(--color-primary))] text-[rgb(var(--color-primary))]' :
                                                isActive ? 'bg-[rgb(var(--color-primary))] border-white/20 text-black animate-pulse' :
                                                    'bg-white/5 border-white/10 text-gray-600'
                                                }`}>
                                                {isCompleted ? (
                                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                                                    </svg>
                                                ) : step.icon}
                                            </div>
                                            <div className={`text-xs font-bold uppercase tracking-tighter transition-colors duration-500 whitespace-nowrap ${isCompleted ? 'text-[rgb(var(--color-primary))]' : isActive ? 'text-[rgb(var(--text-primary))]' : 'text-[rgb(var(--text-secondary))]'
                                                }`}>
                                                {step.label}
                                            </div>
                                        </div>
                                        {index < array.length - 1 && (
                                            <div className="flex-1 h-[2px] mx-4 -mt-8 relative overflow-hidden bg-black/10 dark:bg-white/5">
                                                <div
                                                    className="absolute inset-0 bg-[rgb(var(--color-primary))] transition-all duration-1000 origin-left"
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
            <div className="bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-primary))] rounded-3xl mb-6">
                <div className="flex border-b border-[rgb(var(--border-primary))]">
                    {['status', 'intent-spec', 'components', 'code'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-6 py-4 font-medium transition-colors ${activeTab === tab
                                ? 'border-b-2 border-[rgb(var(--color-primary))] text-[rgb(var(--color-primary))]'
                                : 'text-[rgb(var(--text-secondary))] transition-transform hover:scale-110'
                                }`}
                        >
                            {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div className="glass-card p-6">
                {/* Review Required Integrated Banner */}
                {project.status === 'review_required' && (
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-6 mb-8">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 shrink-0">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-xl font-bold text-yellow-500 mb-1">Review Specification Required</h3>
                                <p className="text-yellow-200/70 mb-4 max-w-2xl text-sm">
                                    {project.intent_spec?.explanation || "The intent prompt was vague. The system has made some intelligent assumptions to move forward. Please review and edit the specification below before proceeding with code generation."}
                                </p>
                                <div className="flex gap-3">
                                    <button
                                        onClick={handleConfirmSpec}
                                        className="px-6 py-2 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 transition-colors"
                                    >
                                        Confirm & Generate
                                    </button>
                                    <button
                                        onClick={() => {
                                            setActiveTab('intent-spec');
                                            setIsEditing(true);
                                        }}
                                        className="px-6 py-2 bg-[rgb(var(--bg-secondary)/0.5)] text-[rgb(var(--text-primary))] font-bold rounded-lg transition-transform hover:scale-105 border border-[rgb(var(--border-primary))]"
                                    >
                                        Edit Spec
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                {activeTab === 'status' && (
                    <div className="space-y-4">
                        <h2 className="text-subtitle font-bold mb-4">Pipeline Status</h2>

                        {project.error_message && (
                            <div className="bg-[rgb(var(--status-error)/0.1)] border border-[rgb(var(--status-error)/0.3)] text-[rgb(var(--status-error))] px-4 py-3 rounded-lg">
                                <strong>Error:</strong> {project.error_message}
                            </div>
                        )}

                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-[rgb(var(--bg-secondary)/0.5)] p-6 rounded-2xl border border-[rgb(var(--border-primary))]">
                                <div className="space-y-3">
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">Project Status</span>
                                        <span className="badge-info">{project.status}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">Current Stage</span>
                                        <span className="text-[rgb(var(--text-primary))] font-medium">{project.current_stage || 'N/A'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">Build Progress</span>
                                        <span className="text-[rgb(var(--text-primary))] font-black">{project.progress}%</span>
                                    </p>
                                </div>
                                <div className="space-y-3">
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">LLM Model</span>
                                        <span className="text-[rgb(var(--color-primary))] font-black uppercase text-[11px]">{project.gemini_model || 'System Default'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">API Key Used</span>
                                        <span className="text-[rgb(var(--color-primary))] font-black uppercase text-[11px]">{project.api_key_name || 'N/A'}</span>
                                    </p>
                                    <p className="flex justify-between items-center text-sm">
                                        <span className="text-label">Started At</span>
                                        <span className="text-[rgb(var(--text-primary))] font-medium text-[11px]">{new Date(project.created_at).toLocaleString()}</span>
                                    </p>
                                    {project.completed_at && (
                                        <p className="flex justify-between items-center text-sm">
                                            <span className="text-label">Finished At</span>
                                            <span className="badge-success">{new Date(project.completed_at).toLocaleString()}</span>
                                        </p>
                                    )}
                                    {project.completed_at && (
                                        <p className="flex justify-between items-center text-sm pt-2 border-t border-[rgb(var(--border-primary))]">
                                            <span className="text-[rgb(var(--text-secondary))] font-bold uppercase tracking-widest text-[10px]">Total Duration</span>
                                            <span className="text-[rgb(var(--color-primary))] font-black text-xs">{getDuration()}</span>
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
                                        ? 'bg-[rgb(var(--status-error)/0.1)] border-[rgb(var(--status-error)/0.3)] text-[rgb(var(--status-error))]'
                                        : 'bg-[rgb(var(--status-info)/0.1)] border-[rgb(var(--status-info)/0.3)] text-[rgb(var(--status-info))]'
                                        }`}
                                >
                                    {isEditing ? 'Cancel Editing' : 'Edit Specification'}
                                </button>
                                {isEditing && (
                                    <button
                                        onClick={handleUpdateSpec}
                                        className="px-4 py-2 bg-[rgb(var(--color-primary))] text-black font-bold rounded-lg hover:opacity-80 transition-all"
                                    >
                                        Save Changes
                                    </button>
                                )}
                            </div>
                        </div>

                        {!project.intent_spec && !isEditing ? (
                            <p className="text-[rgb(var(--text-secondary))]">Intent spec not yet generated</p>
                        ) : isEditing ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Form Column 1: Stack & Features */}
                                <div className="space-y-6">
                                    <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))]">
                                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                            <svg className="w-5 h-5 text-[rgb(var(--color-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                            </svg>
                                            Technology Stack
                                        </h3>
                                        <CustomSelect
                                            label="Backend"
                                            options={[
                                                { value: 'none', label: 'None/Custom' },
                                                { value: 'fastapi', label: 'FastAPI (Python)' },
                                                { value: 'django', label: 'Django (Python)' },
                                                { value: 'express', label: 'Express (Node.js)' },
                                                { value: 'springboot', label: 'Spring Boot (Java)' },
                                            ]}
                                            value={editSpec?.stack?.backend || 'none'}
                                            onChange={val => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, backend: val === 'none' ? null : val } })}
                                        />
                                        <CustomSelect
                                            label="Frontend"
                                            options={[
                                                { value: 'none', label: 'None/API Only' },
                                                { value: 'react', label: 'React (Vite)' },
                                                { value: 'vue', label: 'Vue (Vite)' },
                                                { value: 'nextjs', label: 'Next.js' },
                                            ]}
                                            value={editSpec?.stack?.frontend || 'none'}
                                            onChange={val => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, frontend: val === 'none' ? null : val } })}
                                        />
                                        <CustomSelect
                                            label="Database"
                                            options={[
                                                { value: 'none', label: 'None' },
                                                { value: 'sqlite', label: 'SQLite' },
                                                { value: 'postgres', label: 'PostgreSQL' },
                                                { value: 'mongodb', label: 'MongoDB' },
                                            ]}
                                            value={editSpec?.stack?.database || 'none'}
                                            onChange={val => setEditSpec({ ...editSpec, stack: { ...editSpec.stack, database: val === 'none' ? null : val } })}
                                        />
                                    </div>

                                    <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))]">
                                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                            <svg className="w-5 h-5 text-[rgb(var(--color-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                                                        ? 'bg-[rgb(var(--color-primary))]/20 border-[rgb(var(--color-primary))] text-[rgb(var(--color-primary))]'
                                                        : 'bg-[rgb(var(--bg-secondary)/0.5)] border-[rgb(var(--border-primary))] text-[rgb(var(--text-secondary))]'
                                                        }`}
                                                >
                                                    {feature.replace(/_/g, ' ')}
                                                </button>
                                            ))}
                                            <div className="flex gap-2 w-full mt-2">
                                                <input
                                                    type="text"
                                                    placeholder="Add custom feature..."
                                                    className="flex-1 bg-[rgb(var(--bg-primary)/0.5)] border border-[rgb(var(--border-primary))] rounded-lg p-2 text-sm text-[rgb(var(--text-primary))] focus:outline-none focus:border-[rgb(var(--color-primary))]"
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
                                <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))] h-fit">
                                    <h3 className="text-xl font-bold mb-4 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <svg className="w-5 h-5 text-[rgb(var(--color-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2 2 2 2 2h12c2 0 2-2 2-2V7c0-2-2-2-2-2H6c-2 0-2 2-2 2zm0 5h16" />
                                            </svg>
                                            Data Entities
                                        </div>
                                        <button
                                            onClick={() => setEditSpec({
                                                ...editSpec,
                                                data_entities: [...editSpec.data_entities, { name: 'NewEntity', fields: ['id', 'name'] }]
                                            })}
                                            className="text-xs bg-[rgb(var(--color-primary))] text-[rgb(var(--bg-primary))] px-2 py-1 rounded font-bold"
                                        >
                                            + Add Entity
                                        </button>
                                    </h3>
                                    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                                        {editSpec?.data_entities?.map((entity, idx) => (
                                            <div key={idx} className="p-4 bg-[rgb(var(--bg-primary)/0.3)] rounded-xl border border-[rgb(var(--border-primary)/0.5)] relative group">
                                                <button
                                                    onClick={() => setEditSpec({
                                                        ...editSpec,
                                                        data_entities: editSpec.data_entities.filter((_, i) => i !== idx)
                                                    })}
                                                    className="absolute top-2 right-2 text-[rgb(var(--status-error))] opacity-0 group-hover:opacity-100 transition-opacity"
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
                                                    className="bg-transparent text-[rgb(var(--color-primary))] font-bold border-b border-[rgb(var(--border-primary))] mb-2 focus:outline-none focus:border-[rgb(var(--color-primary))]"
                                                />
                                                <div className="flex flex-wrap gap-1 mb-3">
                                                    {entity.fields.map((field, fIdx) => (
                                                        <span key={fIdx} className="group/tag inline-flex items-center gap-1 px-2 py-0.5 bg-[rgb(var(--bg-primary))] border border-[rgb(var(--color-primary))] text-[rgb(var(--color-primary))] text-[10px] font-bold rounded-full">
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
                                                    className="w-full bg-black/20 border border-white/5 rounded-lg p-2 text-xs text-[rgb(var(--text-primary))] focus:outline-none focus:border-[rgb(var(--color-primary))]"
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
                                <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))] hover:border-[rgb(var(--color-primary)/0.3)] transition-colors">
                                    <div className="badge-gold mb-4 w-fit">Architecture Stack</div>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[rgb(var(--text-secondary))]">Backend</span>
                                            <span className="font-bold text-[rgb(var(--text-primary))]">{project.intent_spec.stack.backend || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[rgb(var(--text-secondary))]">Frontend</span>
                                            <span className="font-bold text-[rgb(var(--text-primary))]">{project.intent_spec.stack.frontend || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[rgb(var(--text-secondary))]">Database</span>
                                            <span className="font-bold text-[rgb(var(--text-primary))]">{project.intent_spec.stack.database || 'None'}</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[rgb(var(--text-secondary))]">Type</span>
                                            <span className="font-bold text-[rgb(var(--text-primary))]">{project.intent_spec.project_type}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))] hover:border-[rgb(var(--color-primary))]/30 transition-colors">
                                    <div className="text-xs font-bold text-[rgb(var(--color-primary))] uppercase tracking-widest mb-4">Derived Features</div>
                                    <div className="flex flex-wrap gap-2">
                                        {project.intent_spec.features.map((f, i) => (
                                            <span key={i} className="px-3 py-1 bg-[rgb(var(--bg-primary))] border border-[rgb(var(--color-secondary))] text-[rgb(var(--color-secondary))] text-[10px] font-bold uppercase rounded-full">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="p-6 bg-[rgb(var(--bg-secondary)/0.5)] rounded-2xl border border-[rgb(var(--border-primary))] hover:border-[rgb(var(--border-primary)/2)] transition-colors">
                                    <div className="text-xs font-bold text-[rgb(var(--text-secondary))] uppercase tracking-widest mb-4">Core Data Models</div>
                                    <div className="space-y-3">
                                        {project.intent_spec.data_entities.slice(0, 4).map((entity, i) => (
                                            <div key={i} className="flex flex-col">
                                                <span className="font-bold text-sm text-[rgb(var(--text-primary))]">{entity.name}</span>
                                                <span className="text-[10px] text-[rgb(var(--text-secondary))] truncate">{entity.fields.join(', ')}</span>
                                            </div>
                                        ))}
                                        {project.intent_spec.data_entities.length > 4 && (
                                            <div className="text-[10px] text-[rgb(var(--color-primary))] font-bold italic">
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
                            <p className="text-body text-[rgb(var(--text-secondary))]">Architecture plan not yet generated</p>
                        )}
                    </div>
                )}

                {activeTab === 'code' && (
                    <div className="animate-fade-in">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-subtitle">Generated Source</h2>
                        </div>
                        <CodePreview projectId={id} />
                    </div>
                )}
            </div>
        </div>
    );
}
