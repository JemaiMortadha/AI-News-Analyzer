import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('access_token'));
    const [loading, setLoading] = useState(true);

    // Configure axios defaults
    axios.defaults.baseURL = 'http://localhost:8000/api';

    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    const response = await axios.get('/auth/profile/');
                    setUser(response.data.user);
                } catch (error) {
                    console.error('Failed to load user', error);
                    logout();
                }
            }
            setLoading(false);
        };

        loadUser();
    }, [token]);

    const login = async (email, password) => {
        try {
            const response = await axios.post('/auth/login/', { email, password });
            const { access, refresh } = response.data.tokens;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            setToken(access);
            setUser(response.data.user);

            axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Login failed'
            };
        }
    };

    const register = async (username, email, password, password2) => {
        try {
            const response = await axios.post('/auth/register/', {
                username,
                email,
                password,
                password2
            });

            const { access, refresh } = response.data.tokens;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            setToken(access);
            setUser(response.data.user);

            axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.password?.[0] || 'Registration failed'
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
