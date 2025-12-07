import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Register = ({ onClose, onSwitchToLogin }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError("Passwords don't match");
            return;
        }

        const result = await register(username, email, password, confirmPassword);
        if (result.success) {
            onClose();
        } else {
            setError(result.error);
        }
    };

    return (
        <div className="auth-modal">
            <div className="auth-content">
                <h2>Create Account</h2>
                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Confirm Password</label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn-primary">Register</button>
                </form>

                <p className="auth-switch">
                    Already have an account?
                    <button onClick={onSwitchToLogin} className="btn-link">Login</button>
                </p>

                <button onClick={onClose} className="btn-close">×</button>
            </div>
        </div>
    );
};

export default Register;
