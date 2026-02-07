import React from 'react';

const PipelineStepper = ({ status }) => {
    const steps = [
        {
            id: 'spec', label: 'Specification',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
            ),
            stages: ['spec_building', 'validating', 'review_required']
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
    ];

    return (
        <div className="mt-10 overflow-x-auto pb-4 custom-scrollbar">
            <div className="flex items-center justify-between min-w-[700px] px-4">
                {steps.map((step, index, array) => {
                    const isCompleted = status === 'completed' ||
                        array.slice(index + 1).some(s => s.stages.includes(status));
                    const isActive = step.stages.includes(status);

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
    );
};

export default PipelineStepper;
