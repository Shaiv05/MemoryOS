"use client";

const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";
const TOKEN_CHANGE_EVENT = "auth-token-changed";

const hasWindow = () => typeof window !== "undefined";

const emitTokenChange = () => {
  if (hasWindow()) {
    window.dispatchEvent(new Event(TOKEN_CHANGE_EVENT));
  }
};

export const getAccessToken = () => {
  if (!hasWindow()) return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = () => {
  if (!hasWindow()) return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setTokens = (accessToken: string, refreshToken: string) => {
  if (!hasWindow()) return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  emitTokenChange();
};

export const clearTokens = () => {
  if (!hasWindow()) return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  emitTokenChange();
};

export const subscribeTokenChanges = (callback: () => void) => {
  if (!hasWindow()) return () => undefined;

  window.addEventListener("storage", callback);
  window.addEventListener(TOKEN_CHANGE_EVENT, callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(TOKEN_CHANGE_EVENT, callback);
  };
};
