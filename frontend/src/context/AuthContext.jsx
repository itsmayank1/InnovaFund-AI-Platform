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

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [role, setRole] = useState(() => user?.role || null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setRole(user?.role || null);
  }, [user]);

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