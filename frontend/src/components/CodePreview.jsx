import React, { useState, useEffect } from 'react';
import Editor from "@monaco-editor/react";
import { projectsAPI } from '../api/client';

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

export default CodePreview;
