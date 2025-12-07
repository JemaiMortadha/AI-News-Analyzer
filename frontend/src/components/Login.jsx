import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import ForgotPassword from './ForgotPassword';

const Login = ({ onClose, onSwitchToRegister }) => {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showForgotPassword, setShowForgotPassword] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(email, password);
        if (result.success) {
            onClose();
        } else {
            setError(result.error);
        }
        setLoading(false);
    };

    if (showForgotPassword) {
        return (
            <ForgotPassword
                onClose={() => setShowForgotPassword(false)}
                onSuccess={() => {
                    setShowForgotPassword(false);
                    onClose();
                }}
            />
        );
    }

    return (
        <div className="auth-modal">
            <div className="auth-content">
                <h2>Login</h2>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div style={{ textAlign: 'right', marginBottom: '1rem' }}>
                        <button
                            type="button"
                            onClick={() => setShowForgotPassword(true)}
                            className="btn-link"
                            style={{ fontSize: '0.9rem', color: 'var(--primary-color)' }}
                        >
                            Forgot password?
                        </button>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <p className="auth-switch">
                    Don't have an account?
                    <button onClick={onSwitchToRegister} className="btn-link">Register</button>
                </p>

                <button onClick={onClose} className="btn-close">×</button>
            </div>
        </div>
    );
};

export default Login;
