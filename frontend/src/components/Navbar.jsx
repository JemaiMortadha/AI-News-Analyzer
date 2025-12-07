import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaUser, FaSignOutAlt, FaMoon, FaSun } from 'react-icons/fa';
import Login from './Login';
import Register from './Register';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showLogin, setShowLogin] = useState(false);
    const [showRegister, setShowRegister] = useState(false);
    const [theme, setTheme] = useState('light'); // To be moved to ThemeContext later

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const toggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light');
        // Implement actual theme switching later
    };

    return (
        <>
            <nav className="navbar">
                <div className="navbar-brand">
                    <Link to="/">AI News Analyzer</Link>
                </div>

                <div className="navbar-menu">
                    <Link to="/" className="nav-item">Home</Link>
                    {user && <Link to="/saved" className="nav-item">Saved</Link>}
                </div>

                <div className="navbar-end">
                    <button className="btn-icon" onClick={toggleTheme}>
                        {theme === 'light' ? <FaMoon /> : <FaSun />}
                    </button>

                    {user ? (
                        <div className="user-menu">
                            <Link to="/profile" className="user-info">
                                <FaUser />
                                <span>{user.username}</span>
                            </Link>
                            <button onClick={handleLogout} className="btn-logout" title="Logout">
                                <FaSignOutAlt />
                            </button>
                        </div>
                    ) : (
                        <div className="auth-buttons">
                            <button onClick={() => setShowLogin(true)} className="btn-login">Login</button>
                            <button onClick={() => setShowRegister(true)} className="btn-register">Register</button>
                        </div>
                    )}
                </div>
            </nav>

            {showLogin && (
                <Login
                    onClose={() => setShowLogin(false)}
                    onSwitchToRegister={() => {
                        setShowLogin(false);
                        setShowRegister(true);
                    }}
                />
            )}

            {showRegister && (
                <Register
                    onClose={() => setShowRegister(false)}
                    onSwitchToLogin={() => {
                        setShowRegister(false);
                        setShowLogin(true);
                    }}
                />
            )}
        </>
    );
};

export default Navbar;
