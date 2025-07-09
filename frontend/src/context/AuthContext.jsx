import React, { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

// You can set VITE_BACKEND_URL in .env (e.g., http://localhost:8000)
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch user from backend session on mount
  useEffect(() => {
    axios
      .get(`${BACKEND_URL}/user`, { withCredentials: true })
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(() => {
        setUser(null);
        setLoading(false);
      });
  }, []);

  // Logout: clears backend session and local user state
  const logout = async () => {
    await axios.get(`${BACKEND_URL}/logout`, { withCredentials: true });
    setUser(null);
    window.location.href = "/";  
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
