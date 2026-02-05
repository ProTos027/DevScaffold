import React, { useState } from 'react';

const AuthPage = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleAuthSuccess = (token) => {
    localStorage.setItem('jwtToken', token); // Store JWT token
    setMessage('Authentication successful! Redirecting...');
    setError('');
    // In a real application, you would redirect the user
    // e.g., navigate('/dashboard');
    setTimeout(() => {
      console.log('User redirected or state updated.');
      // For demonstration, clear form and message after a delay
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setMessage('');
      window.location.reload(); // Simulate full page reload for demo purposes
    }, 1500);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    // Simulate API call
    try {
      // Replace with actual API call (e.g., axios.post('/api/login', { email, password }))
      const response = await new Promise(resolve => setTimeout(() => {
        if (email === 'test@example.com' && password === 'password123') {
          resolve({ success: true, token: 'fake-jwt-token-login' });
        } else {
          resolve({ success: false, message: 'Invalid credentials.' });
        }
      }, 1000));

      if (response.success) {
        handleAuthSuccess(response.token);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    // Simulate API call
    try {
      // Replace with actual API call (e.g., axios.post('/api/register', { email, password }))
      const response = await new Promise(resolve => setTimeout(() => {
        if (email && password) { // Basic validation
          resolve({ success: true, token: 'fake-jwt-token-register' });
        } else {
          resolve({ success: false, message: 'Registration failed. Missing fields.' });
        }
      }, 1000));

      if (response.success) {
        handleAuthSuccess(response.token);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleForm = () => {
    setIsRegistering(!isRegistering);
    setError(''); // Clear error when switching forms
    setMessage('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div style={styles.container}>
      <div style={styles.authBox}>
        <h2 style={styles.title}>{isRegistering ? 'Register' : 'Login'}</h2>

        {error && <p style={styles.error}>{error}</p>}
        {message && <p style={styles.message}>{message}</p>}

        <form onSubmit={isRegistering ? handleRegister : handleLogin} style={styles.form}>
          <div style={styles.formGroup}>
            <label htmlFor="email" style={styles.label}>Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={styles.input}
            />
          </div>
          <div style={styles.formGroup}>
            <label htmlFor="password" style={styles.label}>Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
            />
          </div>
          {isRegistering && (
            <div style={styles.formGroup}>
              <label htmlFor="confirmPassword" style={styles.label}>Confirm Password:</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={styles.input}
              />
            </div>
          )}
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Loading...' : (isRegistering ? 'Register' : 'Login')}
          </button>
        </form>

        <p style={styles.toggleText}>
          {isRegistering ? 'Already have an account?' : "Don't have an account?"}{' '}
          <span onClick={toggleForm} style={styles.toggleLink}>
            {isRegistering ? 'Login' : 'Register'}
          </span>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f0f2f5',
    fontFamily: 'Arial, sans-serif',
  },
  authBox: {
    backgroundColor: '#ffffff',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '400px',
    textAlign: 'center',
  },
  title: {
    marginBottom: '25px',
    color: '#333',
    fontSize: '28px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  formGroup: {
    textAlign: 'left',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: 'bold',
    color: '#555',
  },
  input: {
    width: 'calc(100% - 20px)',
    padding: '12px 10px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    fontSize: '16px',
  },
  button: {
    padding: '12px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    fontSize: '18px',
    cursor: 'pointer',
    marginTop: '20px',
    transition: 'background-color 0.3s ease',
  },
  buttonHover: {
    backgroundColor: '#0056b3',
  },
  error: {
    color: '#dc3545',
    marginBottom: '15px',
    fontWeight: 'bold',
  },
  message: {
    color: '#28a745',
    marginBottom: '15px',
    fontWeight: 'bold',
  },
  toggleText: {
    marginTop: '25px',
    color: '#666',
    fontSize: '15px',
  },
  toggleLink: {
    color: '#007bff',
    textDecoration: 'underline',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
};

export default AuthPage;
