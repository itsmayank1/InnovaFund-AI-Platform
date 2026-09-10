import api from "./api";

export const registerUser = async (data) => {
  const res = await api.post("/auth/register", data);
  return res.data;
};

export const loginUser = async (data) => {
  const res = await api.post("/auth/login", data);
  return res.data;
};

export const googleLogin = async (payload) => {
  // Backend's GoogleAuthRequest accepts either a raw { credential } token string
  // or a plain { email, full_name, role } object. Forward whatever we're given
  // as-is instead of nesting it under a 'credential' key, so both call shapes work.
  const body = typeof payload === "string" ? { credential: payload } : payload;
  const res = await api.post("/auth/google", body);
  return res.data;
};