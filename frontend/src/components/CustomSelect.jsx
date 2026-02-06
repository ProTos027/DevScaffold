import React, { useState, useEffect, useRef } from 'react';

/**
 * CustomSelect - Centralized theme-aware dropdown component.
 * Features:
 * - Perfectly rounded corners (rounded-2xl)
 * - Dynamic z-index management to prevent clipping
 * - Event propagation guards
 * - Theme-integrated primary color accents
 * - Responsive truncation
 */
const CustomSelect = ({
    options,
    value,
    onChange,
    label,
    placeholder = "Select an option",
    className = "",
    labelClassName = "text-gray-400"
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const selectedOption = options.find(opt =>
        (opt.id?.toString() === value?.toString()) ||
        (opt.value?.toString() === value?.toString())
    );

    return (
        <div ref={containerRef} className={`relative w-full group ${isOpen ? 'z-[100]' : 'z-auto'} ${className}`}>
            {label && (
                <label className={`block text-xs font-bold uppercase tracking-widest mb-2 px-1 ${labelClassName}`}>
                    {label}
                </label>
            )}
            <div
                onClick={(e) => {
                    e.stopPropagation();
                    setIsOpen(!isOpen);
                }}
                className={`w-full bg-[rgb(var(--bg-secondary)/0.5)] border border-[rgb(var(--border-primary))] rounded-2xl p-3 text-[rgb(var(--text-primary))] flex justify-between items-center cursor-pointer hover:border-[rgb(var(--color-primary)/0.5)] transition-all ${isOpen ? 'border-[rgb(var(--color-primary))] ring-1 ring-[rgb(var(--color-primary)/0.3)]' : ''}`}
            >
                <span className="truncate text-sm">{selectedOption ? selectedOption.label : placeholder}</span>
                <svg className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180 text-[rgb(var(--color-primary))]' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            {isOpen && (
                <div className="absolute z-[110] w-full mt-2 glass-2 !bg-[rgb(var(--bg-secondary))] !rounded-2xl border border-[rgb(var(--color-primary)/0.3)] shadow-2xl overflow-hidden animate-fade-in py-2">
                    {options.length > 0 ? options.map((opt) => {
                        const optId = opt.id || opt.value;
                        const isSelected = (optId?.toString() === value?.toString());

                        return (
                            <div
                                key={optId}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onChange(optId);
                                    setIsOpen(false);
                                }}
                                className={`px-4 py-2 cursor-pointer transition-colors hover:bg-[rgb(var(--color-primary)/0.1)] hover:text-[rgb(var(--color-primary))] text-sm ${isSelected ? 'bg-[rgb(var(--color-primary)/0.05)] text-[rgb(var(--color-primary))] font-bold' : 'text-[rgb(var(--text-primary))]'}`}
                            >
                                {opt.label}
                            </div>
                        );
                    }) : (
                        <div className="px-6 py-3 text-[rgb(var(--text-secondary))] italic text-sm">No options available</div>
                    )}
                </div>
            )}
        </div>
    );
};

export default CustomSelect;
