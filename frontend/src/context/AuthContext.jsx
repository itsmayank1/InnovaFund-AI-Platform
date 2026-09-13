import { createContext, useContext, useEffect, useState } from "react";
import { loginUser, registerUser, googleLogin as googleLoginApi } from "../services/authService";

function buildUser(data) {
  // data is the TokenResponse payload from the backend: { access_token, user_id, full_name, email, role }
  return {
    id: data.user_id,
    full_name: data.full_name,
    email: data.email,
    role: data.role,
  };
}

// Clear any stored authentication state on reload so each page reload logs out as requested
try {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("user");
} catch (e) {
  // Ignore in case storage access is restricted
}

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setRole(user?.role || null);
  }, [user]);

  // Ensure tokens are removed when window/tab is reloaded or closed
  useEffect(() => {
    const handleBeforeUnload = () => {
      try {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("user");
      } catch (e) {}
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  const applySession = (data) => {
    localStorage.setItem("token", data.access_token);
    const nextUser = buildUser(data);
    localStorage.setItem("user", JSON.stringify(nextUser));
    setToken(data.access_token);
    setUser(nextUser);
    setRole(nextUser.role);
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await loginUser({ email, password });
      applySession(data);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload) => {
    setLoading(true);
    try {
      const data = await registerUser(payload);
      applySession(data);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = async (credential) => {
    setLoading(true);
    try {
      const data = await googleLoginApi(credential);
      applySession(data);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role,
        loading,
        login,
        register,
        googleLogin,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}