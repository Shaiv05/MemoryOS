import api from "./api";

export const registerUser = async (data: {
  username: string;
  email: string;
  password: string;
}) => {
  const res = await api.post("/auth/register/", data);
  return res.data;
};

export const loginUser = async (data: {
  username: string;
  password: string;
}) => {
  const res = await api.post("/auth/login/", data);
  return res.data;
};

export const logoutUser = async (refreshToken: string) => {
  const res = await api.post("/auth/logout/", { refresh: refreshToken });
  return res.data;
};