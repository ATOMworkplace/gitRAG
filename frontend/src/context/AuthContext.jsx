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
    console.log("[DEBUG][AuthContext] Attempting to fetch user from backend:", `${BACKEND_URL}/user`);
    axios
      .get(`${BACKEND_URL}/user`, { withCredentials: true })
      .then((res) => {
        console.log("[DEBUG][AuthContext] Received user from backend:", res.data);
        setUser(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("[DEBUG][AuthContext] Failed to get user:", err, err?.response);
        setUser(null);
        setLoading(false);
      });
  }, []);

  // Logout: clears backend session and local user state
  const logout = async () => {
    console.log("[DEBUG][AuthContext] Logging out via backend:", `${BACKEND_URL}/logout`);
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
