import api from "./api";

export const getMyProfile = async () => {
  const res = await api.get("/profile/me");
  return res.data;
};

export const updateMyProfile = async (data) => {
  const res = await api.put("/profile/me", data);
  return res.data;
};