import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';

// Mock auth_service - In a real application, this would be an actual service file
// imported from a separate module (e.g., import auth_service from '../services/authService';).
/**
 * @typedef {object} RegisterPayload
 * @property {string} email - The user's email address.
 * @property {string} password - The user's chosen password.
 */

/**
 * @typedef {object} RegisterResponse
 * @property {string} message - A success message from the registration.
 * @property {string} userId - The ID of the newly registered user.
 */

/**
 * Mock authentication service to simulate API calls.
 * @namespace auth_service
 */
const auth_service = {
  /**
   * Simulates a user registration API call.
   * @param {RegisterPayload} payload - The registration data (email and password).
   * @returns {Promise<RegisterResponse>} A promise that resolves with registration success or rejects with an error.
   */
  register: async (payload: { email: string; password: string }): Promise<{ message: string; userId: string }> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (payload.email === 'test@example.com') {
          reject(new Error('Email already registered.'));
        } else if (payload.password.length < 6) {
          reject(new Error('Password must be at least 6 characters long.'));
        } else {
          // Simulate successful registration
          resolve({ message: 'Registration successful!', userId: 'user-' + Math.random().toString(36).substr(2, 9) });
        }
      }, 1500); // Simulate network delay
    });
  },
};

/**
 * @typedef {object} RegisterFormData
 * @property {string} email - The email input value.
 * @property {string} password - The password input value.
 * @property {string} confirmPassword - The confirm password input value.
 */

/**
 * RegisterPage functional component.
 *
 * This component displays a user registration form, handles input changes,
 * performs client-side validation, and submits registration data to an
 * authentication service. It manages loading states and displays error/success messages.
 *
 * @returns {JSX.Element} The rendered registration page.
 */
const RegisterPage: React.FC = () => {
  /**
   * State to hold the current values of the form inputs.
   * @type {[RegisterFormData, React.Dispatch<React.SetStateAction<RegisterFormData>>]}
   */
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
  });

  /**
   * State to indicate if a registration request is currently in progress.
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * State to store any error messages, either from client-side validation or API response.
   * @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]}
   */
  const [error, setError] = useState<string | null>(null);

  /**
   * State to store a success message after a successful registration.
   * @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]}
   */
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  /**
   * Handles changes to the form input fields.
   * Updates the `formData` state based on the input's `name` and `value`.
   * @param {ChangeEvent<HTMLInputElement>} e - The change event from the input element.
   */
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
    // Clear error messages if user starts typing again after a password mismatch
    if ((name === 'password' || name === 'confirmPassword') && error === 'Passwords do not match.') {
      setError(null);
    }
  };

  /**
   * Handles the form submission event.
   * Prevents default form submission, performs client-side validation,
   * and calls the `auth_service.register` method.
   * Manages `loading`, `error`, and `successMessage` states throughout the process.
   * @param {FormEvent<HTMLFormElement>} e - The form submission event.
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault(); // Prevent default browser form submission

    setLoading(true);
    setError(null); // Clear previous errors
    setSuccessMessage(null); // Clear previous success messages

    // Client-side validation
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError('All fields are required.');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    try {
      const response = await auth_service.register({
        email: formData.email,
        password: formData.password,
      });
      setSuccessMessage(response.message);
      // Optionally clear the form after successful registration
      setFormData({ email: '', password: '', confirmPassword: '' });
    } catch (err: any) {
      // Handle API errors
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false); // Always stop loading, regardless of success or failure
    }
  };

  // useEffect can be used here for side effects, e.g., redirecting after success,
  // but it's not strictly required for the core responsibilities outlined.
  // Example:
  // useEffect(() => {
  //   if (successMessage) {
  //     // setTimeout(() => navigate('/login'), 2000); // Redirect to login after 2 seconds
  //   }
  // }, [successMessage]);

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px', color: '#333' }}>Register</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
            disabled={loading}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
            disabled={loading}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Confirm Password:</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            required
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
            disabled={loading}
          />
        </div>

        {error && (
          <p style={{ color: '#dc3545', marginBottom: '15px', textAlign: 'center', fontSize: '0.9em' }}>{error}</p>
        )}

        {successMessage && (
          <p style={{ color: '#28a745', marginBottom: '15px', textAlign: 'center', fontSize: '0.9em' }}>{successMessage}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#6c757d' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            transition: 'background-color 0.2s ease-in-out',
          }}
        >
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default RegisterPage;