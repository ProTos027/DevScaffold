import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';

/**
 * @typedef {object} User
 * @property {string} id
 * @property {string} name
 * @property {string} email
 */

/**
 * @typedef {object} AuthContextType
 * @property {User | null} user
 * @property {React.Dispatch<React.SetStateAction<User | null>>} setUser
 * @property {boolean} isLoadingUser
 * @property {string | null} error
 * @property {() => Promise<void>} login
 * @property {() => Promise<void>} logout
 */

/** @type {React.Context<AuthContextType | undefined>} */
const AuthContext = createContext(undefined);

/**
 * Custom hook to use the AuthContext.
 * @returns {AuthContextType}
 * @throws {Error} If used outside an AuthProvider.
 */
const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Provides authentication state and functions to its children.
 * Manages initial user session loading and simulates API calls for login/logout.
 * @param {object} props
 * @param {React.ReactNode} props.children
 * @returns {JSX.Element}
 */
const AuthProvider = ({ children }) => {
  /** @type {[User | null, React.Dispatch<React.SetStateAction<User | null>>]} */
  const [user, setUser] = useState(null);
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setIsLoadingUser(true);
        setError(null);
        // Simulate API call to check for logged-in user (e.g., from localStorage or session)
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay

        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (err) {
        console.error("Failed to fetch user session:", err);
        setError("Failed to load user session.");
      } finally {
        setIsLoadingUser(false);
      }
    };
    fetchUser();
  }, []);

  /**
   * Simulates a login API call.
   * @returns {Promise<void>}
   */
  const login = async () => {
    try {
      setError(null);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      /** @type {User} */
      const loggedInUser = { id: 'user123', name: 'John Doe', email: 'john.doe@example.com' };
      setUser(loggedInUser);
      localStorage.setItem('currentUser', JSON.stringify(loggedInUser));
    } catch (err) {
      setError("Login failed. Please check your credentials.");
      throw err; // Re-throw to allow component to handle specific login errors
    }
  };

  /**
   * Simulates a logout API call.
   * @returns {Promise<void>}
   */
  const logout = async () => {
    try {
      setError(null);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      setUser(null);
      localStorage.removeItem('currentUser');
    } catch (err) {
      setError("Logout failed.");
      throw err;
    }
  };

  /** @type {AuthContextType} */
  const value = { user, setUser, isLoadingUser, error, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Represents the login page.
 * @param {object} props
 * @param {() => void} props.onLoginSuccess - Callback function to execute on successful login.
 * @returns {JSX.Element}
 */
const LoginPage = ({ onLoginSuccess }) => {
  const { login, error: authError, isLoadingUser } = useAuth();
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [email, setEmail] = useState('');
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [password, setPassword] = useState('');
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [localError, setLocalError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);
    setIsLoggingIn(true);
    try {
      await login();
      onLoginSuccess(); // Redirect or perform other actions after successful login
    } catch (err) {
      setLocalError(authError || "An unexpected error occurred during login.");
    } finally {
      setIsLoggingIn(false);
    }
  };

  if (isLoadingUser) return <p style={{ textAlign: 'center', marginTop: '50px' }}>Checking session...</p>;

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '50px auto', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
          />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
          />
        </div>
        {localError && <p style={{ color: 'red', marginBottom: '15px', textAlign: 'center' }}>{localError}</p>}
        <button type="submit" disabled={isLoggingIn} style={{ width: '100%', padding: '12px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px' }}>
          {isLoggingIn ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '20px', textAlign: 'center' }}>Don't have an account? <Link to="/register" style={{ color: '#007bff', textDecoration: 'none' }}>Register</Link></p>
    </div>
  );
};

/**
 * Represents the registration page.
 * @returns {JSX.Element}
 */
const RegisterPage = () => {
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [name, setName] = useState('');
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [email, setEmail] = useState('');
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [password, setPassword] = useState('');
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isRegistering, setIsRegistering] = useState(false);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [error, setError] = useState(null);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsRegistering(true);
    try {
      // Simulate API call for registration
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Assume registration is successful
      setSuccessMessage("Registration successful! You can now log in.");
      setName('');
      setEmail('');
      setPassword('');
    } catch (err) {
      setError("Registration failed. Please try again.");
    } finally {
      setIsRegistering(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '50px auto', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Register</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="name" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Name:</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
          />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
          />
        </div>
        {error && <p style={{ color: 'red', marginBottom: '15px', textAlign: 'center' }}>{error}</p>}
        {successMessage && <p style={{ color: 'green', marginBottom: '15px', textAlign: 'center' }}>{successMessage}</p>}
        <button type="submit" disabled={isRegistering} style={{ width: '100%', padding: '12px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px' }}>
          {isRegistering ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p style={{ marginTop: '20px', textAlign: 'center' }}>Already have an account? <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>Login</Link></p>
    </div>
  );
};

/**
 * Represents the user profile page.
 * @returns {JSX.Element}
 */
const ProfilePage = () => {
  const { user, logout, error: authError } = useAuth();
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [localError, setLocalError] = useState(null);

  const handleLogout = async () => {
    setLocalError(null);
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (err) {
      setLocalError(authError || "An unexpected error occurred during logout.");
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '50px auto', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '25px' }}>Profile Page</h2>
      {user ? (
        <div style={{ fontSize: '1.1em', lineHeight: '1.6' }}>
          <p><strong>ID:</strong> {user.id}</p>
          <p><strong>Name:</strong> {user.name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          {localError && <p style={{ color: 'red', marginTop: '15px', textAlign: 'center' }}>{localError}</p>}
          <button onClick={handleLogout} disabled={isLoggingOut} style={{ width: '100%', padding: '12px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px', marginTop: '30px' }}>
            {isLoggingOut ? 'Logging out...' : 'Logout'}
          </button>
        </div>
      ) : (
        <p style={{ textAlign: 'center', fontSize: '1.1em' }}>You are not logged in. Please <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>login</Link>.</p>
      )}
    </div>
  );
};

/**
 * Defines the common application layout including header, main content, and footer.
 * @param {object} props
 * @param {React.ReactNode} props.children - The content to be rendered within the main area.
 * @param {User | null} props.user - The current authenticated user.
 * @param {boolean} props.isLoadingUser - Indicates if user authentication state is being loaded.
 * @returns {JSX.Element}
 */
const AppLayout = ({ children, user, isLoadingUser }) => {
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f4f7f6' }}>
      <header style={{ backgroundColor: '#333', color: 'white', padding: '15px 25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}>
        <h1 style={{ margin: 0, fontSize: '26px' }}>FrontendApp</h1>
        <nav>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', gap: '25px' }}>
            <li><Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1em', transition: 'color 0.2s' }}>Home</Link></li>
            {isLoadingUser ? (
              <li><span style={{ color: '#ccc' }}>Loading...</span></li>
            ) : user ? (
              <>
                <li><Link to="/profile" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1em', transition: 'color 0.2s' }}>Profile</Link></li>
              </>
            ) : (
              <>
                <li><Link to="/login" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1em', transition: 'color 0.2s' }}>Login</Link></li>
                <li><Link to="/register" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1em', transition: 'color 0.2s' }}>Register</Link></li>
              </>
            )}
          </ul>
        </nav>
      </header>
      <main style={{ flexGrow: 1, padding: '20px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        {children}
      </main>
      <footer style={{ backgroundColor: '#eee', padding: '15px 20px', textAlign: 'center', borderTop: '1px solid #ccc', color: '#555', fontSize: '0.9em' }}>
        <p>&copy; 2023 FrontendApp. All rights reserved.</p>
      </footer>
    </div>
  );
};

/**
 * A private route component that redirects unauthenticated users to the login page.
 * Displays a loading message while authentication state is being determined.
 * @param {object} props
 * @param {React.ReactNode} props.children - The component(s) to render if authenticated.
 * @returns {JSX.Element}
 */
const PrivateRoute = ({ children }) => {
  const { user, isLoadingUser } = useAuth();

  if (isLoadingUser) {
    return <p style={{ textAlign: 'center', marginTop: '50px', fontSize: '1.2em' }}>Loading authentication...</p>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

/**
 * FrontendApp component manages routing, global authentication state,
 * and renders the overall application layout.
 * @returns {JSX.Element} The rendered application.
 */
const FrontendApp = () => {
  const { user, isLoadingUser, error } = useAuth();

  if (isLoadingUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '24px', color: '#333' }}>
        Loading Application...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column', color: 'red', textAlign: 'center', padding: '20px' }}>
        <h2 style={{ marginBottom: '15px' }}>Error: {error}</h2>
        <p style={{ fontSize: '1.1em' }}>A critical error occurred. Please try refreshing the page.</p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <AppLayout user={user} isLoadingUser={isLoadingUser}>
        <Routes>
          {/* Redirect root based on authentication status */}
          <Route path="/" element={user ? <Navigate to="/profile" replace /> : <Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage onLoginSuccess={() => { /* Optionally handle post-login redirect here, e.g., navigate('/profile') */ }} />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <ProfilePage />
              </PrivateRoute>
            }
          />
          {/* Catch-all route for 404 */}
          <Route path="*" element={
            <div style={{ textAlign: 'center', marginTop: '50px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: 'white', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
              <h2 style={{ color: '#dc3545', marginBottom: '15px' }}>404 - Page Not Found</h2>
              <p style={{ fontSize: '1.1em', marginBottom: '20px' }}>The page you are looking for does not exist.</p>
              <Link to="/" style={{ color: '#007bff', textDecoration: 'none', fontSize: '1.1em' }}>Go to Home</Link>
            </div>
          } />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
};

/**
 * A wrapper component to provide the AuthContext to the FrontendApp.
 * This is the component that should be rendered in your root (e.g., index.js/tsx).
 * @returns {JSX.Element}
 */
const AppWrapper = () => (
  <AuthProvider>
    <FrontendApp />
  </AuthProvider>
);

export default AppWrapper;