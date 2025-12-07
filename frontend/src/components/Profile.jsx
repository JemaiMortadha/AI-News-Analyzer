import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const Profile = () => {
    const { user } = useAuth();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [categories, setCategories] = useState([]);

    // Form state
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [notificationEnabled, setNotificationEnabled] = useState(true);
    const [frequency, setFrequency] = useState('daily');

    useEffect(() => {
        fetchProfile();
        fetchCategories();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await axios.get('/auth/profile/');
            const profileData = response.data.profile;
            setProfile(profileData);

            // Initialize form state
            setSelectedCategories(profileData.favorite_categories || []);
            setNotificationEnabled(profileData.notification_enabled);
            setFrequency(profileData.notification_frequency || 'daily');
        } catch (error) {
            console.error('Error fetching profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await axios.get('/news/categories/');
            setCategories(response.data.categories);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setMessage('');

        try {
            await axios.put('/auth/profile/', {
                favorite_categories: selectedCategories,
                notification_enabled: notificationEnabled,
                notification_frequency: frequency
            });
            setMessage('Profile updated successfully!');
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            console.error('Error updating profile:', error);
            setMessage('Failed to update profile.');
        }
    };

    const toggleCategory = (category) => {
        if (selectedCategories.includes(category)) {
            setSelectedCategories(selectedCategories.filter(c => c !== category));
        } else {
            setSelectedCategories([...selectedCategories, category]);
        }
    };

    if (loading) return <div className="loading">Loading profile...</div>;

    return (
        <div className="profile-container">
            <h1>User Profile</h1>

            <div className="profile-section">
                <h2>Account Info</h2>
                <p><strong>Username:</strong> {user?.username}</p>
                <p><strong>Email:</strong> {user?.email}</p>
            </div>

            <form onSubmit={handleSave} className="profile-form">
                <div className="profile-section">
                    <h2>News Preferences</h2>
                    <p>Select your favorite categories:</p>
                    <div className="category-grid">
                        {categories.map(cat => (
                            <label key={cat.value} className={`category-tag ${selectedCategories.includes(cat.value) ? 'active' : ''}`}>
                                <input
                                    type="checkbox"
                                    checked={selectedCategories.includes(cat.value)}
                                    onChange={() => toggleCategory(cat.value)}
                                    style={{ display: 'none' }}
                                />
                                {cat.label}
                            </label>
                        ))}
                    </div>
                </div>

                <div className="profile-section">
                    <h2>Email Notifications</h2>
                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={notificationEnabled}
                                onChange={(e) => setNotificationEnabled(e.target.checked)}
                            />
                            Enable Email Notifications
                        </label>
                    </div>

                    {notificationEnabled && (
                        <div className="form-group">
                            <label>Frequency:</label>
                            <select
                                value={frequency}
                                onChange={(e) => setFrequency(e.target.value)}
                                className="form-select"
                            >
                                <option value="daily">Daily Digest</option>
                                <option value="weekly">Weekly Digest</option>
                            </select>
                        </div>
                    )}
                </div>

                <button type="submit" className="btn-primary save-btn">Save Changes</button>
                {message && <div className={`message ${message.includes('Failed') ? 'error' : 'success'}`}>{message}</div>}
            </form>
        </div>
    );
};

export default Profile;
