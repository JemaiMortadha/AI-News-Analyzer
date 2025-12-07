import React, { useState } from 'react';
import axios from 'axios';

const ForgotPassword = ({ onClose, onSuccess }) => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setMessage('');

        try {
            await axios.post('/auth/password-reset/request/', { email });
            setMessage('Password reset link sent! Please check your email.');
            setTimeout(() => {
                if (onSuccess) onSuccess();
                if (onClose) onClose();
            }, 3000);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to send reset email. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-modal">
            <div className="auth-content">
                <h2>Reset Password</h2>
                <p>Enter your email address and we'll send you a link to reset your password.</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="your@email.com"
                            required
                            disabled={loading}
                        />
                    </div>

                    {error && <div className="error-message">{error}</div>}
                    {message && <div className="success-message">{message}</div>}

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Sending...' : 'Send Reset Link'}
                    </button>
                </form>

                <p className="auth-switch">
                    Remember your password?
                    <button onClick={onClose} className="btn-link">Back to Login</button>
                </p>

                <button onClick={onClose} className="btn-close">×</button>
            </div>
        </div>
    );
};

export default ForgotPassword;
