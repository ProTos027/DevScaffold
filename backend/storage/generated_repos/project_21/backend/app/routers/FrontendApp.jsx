import React, { useState, useEffect, useCallback } from 'react';

/**
 * @typedef {'login' | 'register' | 'profile'} Page - Represents the current page view.
 */

/**
 * @typedef {object} User - Represents a user's profile information.
 * @property {string} id - The unique identifier for the user.
 * @property {string} username - The user's chosen username.
 * @property {string} email - The user's email address.
 * // Add other user profile properties as needed, e.g., firstName, lastName, avatarUrl
 */

/**
 * @typedef {object} LoginCredentials - Data required for user login.
 * @property {string} username - The username for login.
 * @property {string} password - The password for login.
 */

/**
 * @typedef {object} RegisterData - Data required for user registration.
 * @property {string} username - The desired username for registration.
 * @property {string} email - The user's email for registration.
 * @property {string} password - The desired password for registration.
 */

/**
 * @typedef {object} AuthService - Interface for authentication-related API interactions.
 * @property {(credentials: LoginCredentials) => Promise<User>} login - Authenticates a user.
 * @property {(data: RegisterData) => Promise<User>} register - Registers a new user.
 * @property {() => Promise<void>} logout - Logs out the current user.
 */

/**
 * @typedef {object} UserProfileService - Interface for user profile-related API interactions.
 * @property {(userId: string) => Promise<User>} fetchProfile - Fetches a user's profile by ID.
 */

/**
 * @typedef {object} FrontendAppProps - Props for the FrontendApp component.
 * @property {AuthService} authService - Service for authentication operations.
 * @property {UserProfileService} userProfileService - Service for user profile operations.
 */

/**
 * FrontendApp component manages user authentication, registration, and profile display.
 * It interacts with backend APIs via provided service dependencies, handles user input,
 * and manages loading and error states.
 *
 * @param {FrontendAppProps} props - The props for the component.
 * @returns {JSX.Element} The rendered React component.
 */
function FrontendApp({ authService, userProfileService }) {
  /** @type {Page} */
  const [currentPage, setCurrentPage] = useState('login');
  /** @type {User | null} */
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });

  /**
   * Handles changes in form input fields, updating the formData state.
   * @param {React.ChangeEvent<HTMLInputElement>} e - The change event from the input element.
   */
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  }, []);

  /**
   * Navigates the application to a specified page, clearing errors and form data.
   * @param {Page} page - The target page ('login', 'register', or 'profile').
   */
  const navigateTo = useCallback((page) => {
    setCurrentPage(page);
    setError(''); // Clear any previous errors
    setFormData({ username: '', email: '', password: '' }); // Clear form data on page change
  }, []);

  /**
   * Handles the submission of the login form.
   * Interacts with the authService to authenticate the user.
   * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
   */
  const handleLoginSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      /** @type {LoginCredentials} */
      const credentials = { username: formData.username, password: formData.password };
      const loggedInUser = await authService.login(credentials);
      setUser(loggedInUser);
      navigateTo('profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred during login.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  }, [formData.username, formData.password, authService, navigateTo]);

  /**
   * Handles the submission of the registration form.
   * Interacts with the authService to register a new user.
   * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
   */
  const handleRegisterSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      /** @type {RegisterData} */
      const registerData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      };
      const registeredUser = await authService.register(registerData);
      setUser(registeredUser);
      navigateTo('profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred during registration.');
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  }, [formData.username, formData.email, formData.password, authService, navigateTo]);

  /**
   * Handles the user logout process.
   * Interacts with the authService to log out the user and clears user state.
   */
  const handleLogout = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      await authService.logout();
      setUser(null);
      navigateTo('login');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred during logout.');
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  }, [authService, navigateTo]);

  // useEffect to potentially check for an existing session or token on component mount
  // and fetch user profile if available. (Currently commented out for simplicity,
  // as user is set directly after login/register in this example.)
  useEffect(() => {
    // Example: Check for a token in localStorage and try to fetch user profile
    // if (localStorage.getItem('authToken') && !user) {
    //   const fetchCurrentProfile = async () => {
    //     setLoading(true);
    //     try {
    //       // In a real app, you'd decode the token to get a userId or have a /me endpoint
    //       const fetchedUser = await userProfileService.fetchProfile('currentUserIdFromToken');
    //       setUser(fetchedUser);
    //       setCurrentPage('profile');
    //     } catch (err) {
    //       console.error('Failed to fetch profile on mount:', err);
    //       setError('Session expired or invalid. Please log in again.');
    //       localStorage.removeItem('authToken'); // Clear invalid token
    //       setCurrentPage('login');
    //     } finally {
    //       setLoading(false);
    //     }
    //   };
    //   fetchCurrentProfile();
    // }
  }, [user, userProfileService]); // userProfileService is a dependency, but its direct usage is commented out.

  return (
    <div className="frontend-app-container" style={{ fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Frontend Application</h1>

      {loading && <p style={{ color: 'blue', textAlign: 'center' }}>Loading...</p>}
      {error && <p style={{ color: 'red', textAlign: 'center', border: '1px solid red', padding: '10px', borderRadius: '4px', backgroundColor: '#ffe6e6' }}>Error: {error}</p>}

      <nav style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
        {!user && <button onClick={() => navigateTo('login')} disabled={currentPage === 'login' || loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: currentPage === 'login' ? '#0056b3' : '#007bff', color: 'white' }}>Login</button>}
        {!user && <button onClick={() => navigateTo('register')} disabled={currentPage === 'register' || loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: currentPage === 'register' ? '#0056b3' : '#007bff', color: 'white' }}>Register</button>}
        {user && <button onClick={() => navigateTo('profile')} disabled={currentPage === 'profile' || loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: currentPage === 'profile' ? '#28a745' : '#218838', color: 'white' }}>Profile</button>}
        {user && <button onClick={handleLogout} disabled={loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: '#dc3545', color: 'white' }}>Logout</button>}
      </nav>

      {currentPage === 'login' && !user && (
        <section className="login-page" style={{ padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2 style={{ textAlign: 'center', color: '#333' }}>Login</h2>
          <form onSubmit={handleLoginSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div>
              <label htmlFor="login-username" style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
              <input
                type="text"
                id="login-username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="login-password" style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
              <input
                type="password"
                id="login-password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <button type="submit" disabled={loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', fontSize: '16px' }}>Login</button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '15px' }}>Don't have an account? <button onClick={() => navigateTo('register')} disabled={loading} style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}>Register here</button></p>
        </section>
      )}

      {currentPage === 'register' && !user && (
        <section className="registration-page" style={{ padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2 style={{ textAlign: 'center', color: '#333' }}>Register</h2>
          <form onSubmit={handleRegisterSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div>
              <label htmlFor="register-username" style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
              <input
                type="text"
                id="register-username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="register-email" style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
              <input
                type="email"
                id="register-email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="register-password" style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
              <input
                type="password"
                id="register-password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
              />
            </div>
            <button type="submit" disabled={loading} style={{ padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', fontSize: '16px' }}>Register</button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '15px' }}>Already have an account? <button onClick={() => navigateTo('login')} disabled={loading} style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}>Login here</button></p>
        </section>
      )}

      {currentPage === 'profile' && user && (
        <section className="user-profile-page" style={{ padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h2 style={{ textAlign: 'center', color: '#333' }}>User Profile</h2>
          <div style={{ lineHeight: '1.8' }}>
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            {/* Add more profile details here as needed */}
          </div>
          <button onClick={handleLogout} disabled={loading} style={{ display: 'block', width: '100%', padding: '10px 15px', border: 'none', borderRadius: '5px', cursor: 'pointer', backgroundColor: '#dc3545', color: 'white', fontSize: '16px', marginTop: '20px' }}>Logout</button>
        </section>
      )}
    </div>
  );
}

export default FrontendApp;