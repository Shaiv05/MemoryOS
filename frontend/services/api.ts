import axios from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/lib/token-storage";

const api = axios.create({
  baseURL: (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api").replace(/\/+$/, ""),
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (config.url?.startsWith("/")) {
    config.url = config.url.slice(1);
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"];
  }

  return config;
});

interface FailedRequest {
  resolve: (token: string | null) => void;
  reject: (error: unknown) => void;
}

let isRefreshing = false;
let failedQueue: FailedRequest[] = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check if error response is 401 and we haven't already retried this request
    if (error.response?.status === 401 && !originalRequest._retry) {
      // If the error was from the refresh endpoint itself, fail immediately
      if (originalRequest.url?.includes("/auth/refresh/") || originalRequest.url?.includes("auth/refresh/") || originalRequest.url?.includes("/auth/refresh") || originalRequest.url?.includes("auth/refresh")) {
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        isRefreshing = false;
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      try {
        // Notice we call Django backend at /auth/refresh/ (which translates to baseURL + /auth/refresh/ since api has custom slash handling, or we can use axios directly)
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh/`,
          { refresh: refreshToken }
        );
        const { access, refresh } = response.data;
        // SimpleJWT TokenRefreshView returns rotated refresh token if ROTATE_REFRESH_TOKENS=True
        setTokens(access, refresh || refreshToken);
        processQueue(null, access);
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
