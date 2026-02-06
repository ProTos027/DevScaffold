import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import ProjectPage from './pages/ProjectPage';
import GitHubCallback from './pages/GitHubCallback';

// Simple PrivateRoute component
const PrivateRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center border-none">
                <div className="text-2xl font-display text-[rgb(var(--color-primary))] animate-pulse">Initializing...</div>
            </div>
        );
    }

    return isAuthenticated ? children : <Navigate to="/" />;
};

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <Router>
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/login" element={<LandingPage />} />
                        <Route
                            path="/dashboard"
                            element={
                                <PrivateRoute>
                                    <DashboardPage />
                                </PrivateRoute>
                            }
                        />
                        <Route
                            path="/project/:id"
                            element={
                                <PrivateRoute>
                                    <ProjectPage />
                                </PrivateRoute>
                            }
                        />
                        <Route path="/auth/github/callback" element={<GitHubCallback />} />
                    </Routes>
                </Router>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
