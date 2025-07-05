import React, { createContext, useState, useEffect } from 'react';

// Create the AuthContext with default values
const AuthContext = createContext({
  user: null,
  login: () => {},
  register: () => {},
  logout: () => {},
  loading: true,
});

// AuthProvider component to wrap your app and provide auth state/functions
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, try to load user from localStorage or some persistent storage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // Login function (replace with real API call in production)
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  // Register function (example, you can extend it)
  const register = (userData) => {
    // Registration logic here (API call etc)
    login(userData); // For example, auto login after registering
  };

  // Logout function clears user data
  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
