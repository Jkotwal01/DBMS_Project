import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const response = await api.get("/auth/me");
        setUser(response.data);
        // Redirect to appropriate dashboard if on login/register page
        const currentPath = window.location.pathname;
        if (
          currentPath === "/login" ||
          currentPath === "/register" ||
          currentPath === "/"
        ) {
          const role = response.data.role.toLowerCase();
          navigate(`/${role}/dashboard`, { replace: true });
        }
      } catch (error) {
        logout();
      }
    }
    setLoading(false);
  };

  const login = async (credentials) => {
    const response = await api.post("/login", new URLSearchParams(credentials));
    const token = response.data.access_token;
    localStorage.setItem("token", token);
    await checkAuth();
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login", { replace: true });
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
