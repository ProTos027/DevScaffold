import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function GitHubCallback() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    useEffect(() => {
        const handleCallback = () => {
            // Get JWT tokens from URL params (provided by backend after GitHub OAuth)
            const access = searchParams.get('access');
            const refresh = searchParams.get('refresh');

            if (!access || !refresh) {
                console.error('Missing tokens in callback');
                navigate('/login?error=github_auth_failed');
                return;
            }

            // Store JWT tokens
            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);

            // Force reload to dashboard to trigger auth context update
            window.location.href = '/dashboard';
        };

        handleCallback();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center p-8 glass-card border-none">
                <div className="text-2xl font-display text-cosmic-cyan animate-pulse mb-6 tracking-widest">
                    SYNCHRONIZING SECURE ACCESS...
                </div>
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cosmic-cyan mx-auto"></div>
            </div>
        </div>
    );
}
