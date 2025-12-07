import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import ArticlesList from './components/ArticlesList';
import Profile from './components/Profile';
import DemoPage from './components/DemoPage';
import ResetPassword from './components/ResetPassword';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading">Loading...</div>;
  if (!user) return <Navigate to="/" />;

  return children;
};

const AppContent = () => {
  const location = useLocation();
  const isDemoPage = location.pathname === '/demo';
  const isResetPasswordPage = location.pathname.startsWith('/reset-password/');

  // Render reset password modal outside normal layout
  if (isResetPasswordPage) {
    return <ResetPassword />;
  }

  return (
    <div className="app-container">
      {!isDemoPage && <Navbar />}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ArticlesList />} />
          <Route path="/demo" element={<DemoPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/saved"
            element={
              <ProtectedRoute>
                <ArticlesList filter="saved" />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;