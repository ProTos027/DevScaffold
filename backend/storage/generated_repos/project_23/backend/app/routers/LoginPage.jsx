import React, { useState } from 'react';

// Mock auth_service for demonstration purposes.
// In a real application, this would be an external module or a service injected.
const auth_service = {
  /**
   * Simulates an API call to log in a user.
   * @param {string} username - The user's username or email.
   * @param {string} password - The user's password.
   * @returns {Promise<{token: string}>} A promise that resolves with an auth token on success.
   */
  login: async (username, password) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (username === 'user' && password === 'password') {
          resolve({ token: 'mock_auth_token_123' });
        } else {
          reject(new Error('Invalid username or password.'));
        }
      }, 1500); // Simulate network delay
    });
  },

  /**
   * Stores the authentication token in local storage.
   * @param {string} token - The authentication token to store.
   * @returns {void}
   */
  storeToken: (token) => {
    localStorage.setItem('authToken', token);
    console.log('Auth token stored:', token);
  },

  /**
   * Retrieves the authentication token from local storage.
   * @returns {string | null} The authentication token, or null if not found.
   */
  getToken: () => {
    return localStorage.getItem('authToken');
  },

  /**
   * Removes the authentication token from local storage.
   * @returns {void}
   */
  removeToken: () => {
    localStorage.removeItem('authToken');
    console.log('Auth token removed.');
  }
};

/**
 * @typedef {object} LoginPageProps
 * @property {() => void} [onLoginSuccess] - Optional callback function to be called upon successful login.
 */

/**
 * A React functional component for displaying a login form, handling login submission,
 * and storing the authentication token upon success.
 *
 * @param {LoginPageProps} props - The properties for the LoginPage component.
 * @returns {JSX.Element} The LoginPage component.
 */
const LoginPage = ({ onLoginSuccess }) => {
  /**
   * @type {[string, React.Dispatch<React.SetStateAction<string>>]}
   */
  const [username, setUsername] = useState('');
  /**
   * @type {[string, React.Dispatch<React.SetStateAction<string>>]}
   */
  const [password, setPassword] = useState('');
  /**
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [isLoading, setIsLoading] = useState(false);
  /**
   * @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]}
   */
  const [error, setError] = useState(null);
  /**
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  /**
   * Handles the change event for input fields.
   * @param {React.ChangeEvent<HTMLInputElement>} e - The change event.
   * @returns {void}
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'username') {
      setUsername(value);
    } else if (name === 'password') {
      setPassword(value);
    }
    // Clear any previous error message when the user starts typing again
    if (error) setError(null);
  };

  /**
   * Handles the form submission for login.
   * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
   * @returns {Promise<void>}
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null); // Clear previous errors
    setIsLoggedIn(false); // Reset login status

    try {
      const { token } = await auth_service.login(username, password);
      auth_service.storeToken(token); // Store the authentication token
      setIsLoggedIn(true); // Indicate successful login
      if (onLoginSuccess) {
        onLoginSuccess(); // Call the success callback if provided
      }
      // Optionally clear form fields after successful login
      setUsername('');
      setPassword('');
    } catch (err) {
      /** @type {Error} */
      const loginError = err;
      setError(loginError.message || 'An unexpected error occurred during login.');
      console.error('Login error:', loginError);
    } finally {
      setIsLoading(false); // Always stop loading, regardless of success or failure
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ textAlign: 'center', color: '#333', marginBottom: '25px' }}>Login</h2>

      {isLoggedIn && (
        <p style={{ color: 'green', fontWeight: 'bold', textAlign: 'center', marginBottom: '15px' }}>
          Login successful!
        </p>
      )}

      {error && (
        <p style={{ color: 'red', textAlign: 'center', marginBottom: '15px' }}>{error}</p>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#555' }}>Username:</label>
          <input
            type="text"
            id="username"
            name="username"
            value={username}
            onChange={handleChange}
            disabled={isLoading}
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box', fontSize: '16px' }}
            required
            aria-label="Username"
          />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#555' }}>Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={password}
            onChange={handleChange}
            disabled={isLoading}
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box', fontSize: '16px' }}
            required
            aria-label="Password"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || isLoggedIn}
          style={{
            width: '100%',
            padding: '12px 15px',
            backgroundColor: isLoading || isLoggedIn ? '#cccccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading || isLoggedIn ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            fontWeight: 'bold',
            transition: 'background-color 0.2s ease'
          }}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '25px', fontSize: '0.9em', color: '#666', textAlign: 'center' }}>
        Hint: Try username "user" and password "password"
      </p>
    </div>
  );
};

export default LoginPage;