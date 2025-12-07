import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { FaUser, FaSignOutAlt } from 'react-icons/fa';
import Login from './Login';
import Register from './Register';

const Navbar = () => {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const [showLogin, setShowLogin] = useState(false);
    const [showRegister, setShowRegister] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/');
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
                    <button onClick={toggleTheme} className="btn-theme" title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
                        {theme === 'light' ? '🌙' : '☀️'}
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
                        <button onClick={() => setShowLogin(true)} className="btn-icon-login" title="Login">
                            <FaUser />
                        </button>
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
