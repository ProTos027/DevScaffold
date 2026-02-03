import React, { useState, useEffect } from 'react';

/**
 * @typedef {object} UserProfile
 * @property {string} id - The unique identifier for the user.
 * @property {string} name - The user's full name.
 * @property {string} email - The user's email address.
 * @property {string} bio - A short biography of the user.
 */

/**
 * Mock user profile service to simulate API calls.
 * In a real application, this would be an actual service file,
 * likely imported from a separate module.
 */
const user_profile_service = {
  /**
   * Fetches the user profile data from a simulated API.
   * @returns {Promise<UserProfile>} A promise that resolves with the user profile data.
   */
  fetchUserProfile: async () => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate a successful fetch
        resolve({
          id: 'user-123',
          name: 'Jane Doe',
          email: 'jane.doe@example.com',
          bio: 'Passionate software developer with a focus on front-end technologies and user experience.',
        });
        // Uncomment the line below to simulate a fetch error
        // reject(new Error('Failed to fetch user profile data.'));
      }, 1000); // Simulate network delay
    });
  },

  /**
   * Updates the user profile data via a simulated API.
   * @param {UserProfile} profileData - The profile data to update.
   * @returns {Promise<UserProfile>} A promise that resolves with the updated user profile data.
   */
  updateUserProfile: async (profileData) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate a successful update
        resolve({ ...profileData });
        // Uncomment the line below to simulate an update error
        // reject(new Error('Failed to update user profile. Please try again.'));
      }, 800); // Simulate network delay
    });
  },
};

/**
 * ProfilePage component is responsible for displaying user profile data,
 * handling profile updates, and fetching the user's profile data.
 *
 * @returns {JSX.Element} The ProfilePage component.
 */
const ProfilePage = () => {
  /**
   * @type {[UserProfile | null, React.Dispatch<React.SetStateAction<UserProfile | null>>]}
   */
  const [profile, setProfile] = useState(null);
  /**
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [loading, setLoading] = useState(true);
  /**
   * @type {[string | null, React.Dispatch<React.SetStateAction<string | null>>]}
   */
  const [error, setError] = useState(null);
  /**
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [isEditing, setIsEditing] = useState(false);
  /**
   * @type {[UserProfile | null, React.Dispatch<React.SetStateAction<UserProfile | null>>]}
   */
  const [formData, setFormData] = useState(null);

  /**
   * useEffect hook to fetch user profile data when the component mounts.
   */
  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError(null); // Clear any previous errors
      try {
        const data = await user_profile_service.fetchUserProfile();
        setProfile(data);
        setFormData(data); // Initialize form data with fetched profile
      } catch (err) {
        /** @type {Error} */
        const fetchError = err;
        setError(fetchError.message || 'An unknown error occurred while fetching profile.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []); // Empty dependency array ensures this runs only once on mount

  /**
   * Handles changes in the form input fields when in edit mode.
   * @param {React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>} e - The change event object.
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => (prevData ? { ...prevData, [name]: value } : null));
  };

  /**
   * Handles the submission of the profile update form.
   * @param {React.FormEvent<HTMLFormElement>} e - The form submission event object.
   */
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!formData) return;

    setLoading(true);
    setError(null); // Clear any previous errors
    try {
      const updatedData = await user_profile_service.updateUserProfile(formData);
      setProfile(updatedData);
      setIsEditing(false); // Exit edit mode on successful update
    } catch (err) {
      /** @type {Error} */
      const updateError = err;
      setError(updateError.message || 'An unknown error occurred while updating profile.');
    } finally {
      setLoading(false);
    }
  };

  // Conditional rendering for loading, error, and no profile states
  if (loading && !profile) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', fontSize: '1.2em', color: '#555', fontFamily: 'Arial, sans-serif' }}>
        Loading profile...
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', fontSize: '1.2em', color: 'red', fontFamily: 'Arial, sans-serif' }}>
        Error: {error}
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', fontSize: '1.2em', color: '#777', fontFamily: 'Arial, sans-serif' }}>
        No profile data available.
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', padding: '20px', border: '1px solid #e0e0e0', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', fontFamily: 'Arial, sans-serif', backgroundColor: '#fff' }}>
      <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '30px' }}>User Profile</h1>

      {/* Display loading and error messages during updates */}
      {loading && profile && <p style={{ textAlign: 'center', color: '#007bff', marginBottom: '15px' }}>Updating profile...</p>}
      {error && profile && <p style={{ textAlign: 'center', color: 'red', marginBottom: '15px' }}>Error: {error}</p>}

      {isEditing ? (
        <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label htmlFor="name" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData?.name || ''}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '12px', border: '1px solid #ccc', borderRadius: '6px', fontSize: '1em', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label htmlFor="email" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData?.email || ''}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '12px', border: '1px solid #ccc', borderRadius: '6px', fontSize: '1em', boxSizing: 'border-box' }}
            />
          </div>
          <div>
            <label htmlFor="bio" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Bio:</label>
            <textarea
              id="bio"
              name="bio"
              value={formData?.bio || ''}
              onChange={handleChange}
              rows="5"
              style={{ width: '100%', padding: '12px', border: '1px solid #ccc', borderRadius: '6px', fontSize: '1em', boxSizing: 'border-box', resize: 'vertical' }}
            ></textarea>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '15px', marginTop: '20px' }}>
            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                setFormData(profile); // Revert form data to current profile if cancelling
                setError(null); // Clear any errors when cancelling
              }}
              disabled={loading}
              style={{ padding: '12px 25px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#6c757d', color: 'white', fontSize: '1em', transition: 'background-color 0.2s' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{ padding: '12px 25px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', fontSize: '1em', transition: 'background-color 0.2s' }}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <p style={{ fontSize: '1.1em', color: '#333' }}><strong>Name:</strong> {profile.name}</p>
          <p style={{ fontSize: '1.1em', color: '#333' }}><strong>Email:</strong> {profile.email}</p>
          <p style={{ fontSize: '1.1em', color: '#333' }}><strong>Bio:</strong> {profile.bio}</p>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button
              onClick={() => {
                setIsEditing(true);
                setFormData(profile); // Ensure form data is current profile when entering edit mode
                setError(null); // Clear any errors when entering edit mode
              }}
              disabled={loading}
              style={{ padding: '12px 25px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#28a745', color: 'white', fontSize: '1em', transition: 'background-color 0.2s' }}
            >
              Edit Profile
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;