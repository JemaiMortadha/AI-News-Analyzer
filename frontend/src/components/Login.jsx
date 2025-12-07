import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Login = ({ onClose, onSwitchToRegister }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const result = await login(email, password);
        if (result.success) {
            onClose();
        } else {
            setError(result.error);
        }
    };

    return (
        <div className="auth-modal">
            <div className="auth-content">
                <h2>Login</h2>
                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
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

                    <button type="submit" className="btn-primary">Login</button>
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
