import React, { useState, useEffect } from 'react';

/**
 * @typedef {object} User
 * @property {string} id
 * @property {string} username
 * @property {string} email
 * @property {string} [firstName]
 * @property {string} [lastName]
 */

/**
 * @typedef {object} AuthCredentials
 * @property {string} username
 * @property {string} password
 */

/**
 * @typedef {object} AuthService
 * @property {function(): Promise<{ isLoggedIn: boolean, user: User | null }>} checkAuthStatus - Checks current authentication status.
 * @property {(credentials: AuthCredentials) => Promise<User>} login - Authenticates a user with credentials.
 * @property {function(): Promise<void>} logout - Logs out the current user.
 */

/**
 * @typedef {object} UserProfileService
 * @property {(userId: string) => Promise<User>} fetchUserProfile - Fetches a user's profile by ID.
 * @property {(userId: string, updates: Partial<User>) => Promise<User>} updateUserProfile - Updates a user's profile.
 */

// Assume `auth_service` and `user_profile_service` are imported from a separate module.
// For demonstration purposes, mock implementations are provided here.
// In a real application, these would typically be:
// import * as auth_service from './services/auth';
// import * as user_profile_service from './services/user';

/** @type {AuthService} */
const auth_service = {
  checkAuthStatus: async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
          resolve({ isLoggedIn: true, user: JSON.parse(storedUser) });
        } else {
          resolve({ isLoggedIn: false, user: null });
        }
      }, 500); // Simulate API call
    });
  },
  login: async (credentials) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (credentials.username === 'user' && credentials.password === 'pass') {
          const user = { id: '1', username: 'user', email: 'user@example.com', firstName: 'Test', lastName: 'User' };
          localStorage.setItem('currentUser', JSON.stringify(user));
          resolve(user);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 700); // Simulate API call
    });
  },
  logout: async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        localStorage.removeItem('currentUser');
        resolve();
      }, 300); // Simulate API call
    });
  }
};

/** @type {UserProfileService} */
const user_profile_service = {
  fetchUserProfile: async (userId) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser && JSON.parse(storedUser).id === userId) {
          resolve(JSON.parse(storedUser));
        } else {
          reject(new Error('User not found'));
        }
      }, 400); // Simulate API call
    });
  },
  updateUserProfile: async (userId, updates) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser && JSON.parse(storedUser).id === userId) {
          const updatedUser = { ...JSON.parse(storedUser), ...updates };
          localStorage.setItem('currentUser', JSON.stringify(updatedUser));
          resolve(updatedUser);
        } else {
          reject(new Error('User not found or not authorized to update'));
        }
      }, 600); // Simulate API call
    });
  }
};

/**
 * Renders the login form.
 * @param {object} props
 * @param {(credentials: AuthCredentials) => Promise<void>} props.onLogin - Function to call on login attempt.
 * @param {boolean} props.isLoading - Indicates if a login attempt is in progress.
 * @param {string | null} props.error - Error message to display.
 * @returns {JSX.Element} The LoginPage component.
 */
const LoginPage = ({ onLogin, isLoading, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onLogin({ username, password });
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', maxWidth: '400px', margin: '50px auto' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={isLoading} style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '20px', fontSize: '0.9em', color: '#666' }}>
        Hint: Use username "user" and password "pass" to log in.
      </p>
    </div>
  );
};

/**
 * Renders the user profile page.
 * @param {object} props
 * @param {User} props.user - The authenticated user object.
 * @param {function(): Promise<void>} props.onLogout - Function to call on logout.
 * @param {boolean} props.isLoading - Indicates if a logout attempt is in progress.
 * @param {string | null} props.error - Error message to display.
 * @returns {JSX.Element} The UserProfilePage component.
 */
const UserProfilePage = ({ user, onLogout, isLoading, error }) => {
  const [profileData, setProfileData] = useState(user);
  const [isEditing, setIsEditing] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState(null);

  useEffect(() => {
    setProfileData(user);
  }, [user]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setUpdateLoading(true);
    setUpdateError(null);
    try {
      if (profileData && profileData.id) {
        const updatedUser = await user_profile_service.updateUserProfile(profileData.id, profileData);
        setProfileData(updatedUser);
        setIsEditing(false);
      }
    } catch (err) {
      setUpdateError(err.message || 'Failed to update profile.');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', maxWidth: '600px', margin: '50px auto' }}>
      <h2>Welcome, {user.firstName || user.username}!</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {updateError && <p style={{ color: 'red' }}>{updateError}</p>}

      {isEditing ? (
        <form onSubmit={handleProfileUpdate}>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
            <input type="text" name="username" value={profileData?.username || ''} onChange={handleChange} disabled={updateLoading} style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }} />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
            <input type="email" name="email" value={profileData?.email || ''} onChange={handleChange} disabled={updateLoading} style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }} />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>First Name:</label>
            <input type="text" name="firstName" value={profileData?.firstName || ''} onChange={handleChange} disabled={updateLoading} style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }} />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Last Name:</label>
            <input type="text" name="lastName" value={profileData?.lastName || ''} onChange={handleChange} disabled={updateLoading} style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }} />
          </div>
          <button type="submit" disabled={updateLoading} style={{ padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>
            {updateLoading ? 'Saving...' : 'Save Profile'}
          </button>
          <button type="button" onClick={() => setIsEditing(false)} disabled={updateLoading} style={{ padding: '10px 15px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Cancel
          </button>
        </form>
      ) : (
        <div>
          <p><strong>ID:</strong> {user.id}</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>First Name:</strong> {user.firstName || 'N/A'}</p>
          <p><strong>Last Name:</strong> {user.lastName || 'N/A'}</p>
          <button onClick={() => setIsEditing(true)} style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>
            Edit Profile
          </button>
        </div>
      )}
      <button onClick={onLogout} disabled={isLoading} style={{ padding: '10px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '20px' }}>
        {isLoading ? 'Logging out...' : 'Logout'}
      </button>
    </div>
  );
};

/**
 * FrontendApp component manages client-side authentication state,
 * interacts with backend APIs for auth and user profiles,
 * and renders authentication or user profile pages accordingly.
 *
 * @returns {JSX.Element} The FrontendApp component.
 */
const FrontendApp = () => {
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  /** @type {[User | null, React.Dispatch<React.SetStateAction<User | null>>]} */
  const [user, setUser] = useState(null);
  /** @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]} */
  const [isLoading, setIsLoading] = useState(true);
  /** @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]} */
  const [error, setError] = useState(null);

  /**
   * Checks the authentication status on component mount.
   */
  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const { isLoggedIn: status, user: userData } = await auth_service.checkAuthStatus();
        setIsLoggedIn(status);
        setUser(userData);
      } catch (err) {
        setError(err.message || 'Failed to check authentication status.');
        setIsLoggedIn(false);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Handles user login.
   * @param {AuthCredentials} credentials - User login credentials.
   */
  const handleLogin = async (credentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const userData = await auth_service.login(credentials);
      setIsLoggedIn(true);
      setUser(userData);
    } catch (err) {
      setError(err.message || 'Login failed.');
      setIsLoggedIn(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handles user logout.
   */
  const handleLogout = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await auth_service.logout();
      setIsLoggedIn(false);
      setUser(null);
    } catch (err) {
      setError(err.message || 'Logout failed.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <p>Loading application...</p>
        <div style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #3498db', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite', margin: '20px auto' }}></div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="frontend-app">
      <h1 style={{ textAlign: 'center', color: '#333' }}>Frontend Application</h1>
      {error && <p style={{ color: 'red', textAlign: 'center' }}>Error: {error}</p>}

      {isLoggedIn && user ? (
        <UserProfilePage user={user} onLogout={handleLogout} isLoading={isLoading} error={error} />
      ) : (
        <LoginPage onLogin={handleLogin} isLoading={isLoading} error={error} />
      )}
    </div>
  );
};

export default FrontendApp;