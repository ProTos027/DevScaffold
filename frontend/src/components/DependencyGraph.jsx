import React, { useMemo } from 'react';
import ReactFlow, { Controls, MarkerType } from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';

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
            <div className="w-full h-[550px] bg-[rgb(var(--bg-secondary))] rounded-2xl border border-[rgb(var(--border-primary))] overflow-hidden relative">
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

export default DependencyGraph;
