"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import {
  clearTokens,
  getAccessToken,
  subscribeTokenChanges,
} from "@/lib/token-storage";

type UseAuthOptions = {
  required?: boolean;
};

export function useAuth(options: UseAuthOptions = {}) {
  const router = useRouter();
  const token = useSyncExternalStore(
    subscribeTokenChanges,
    getAccessToken,
    () => null
  );

  useEffect(() => {
    if (options.required && !token) {
      router.replace("/login");
    }
  }, [options.required, router, token]);

  const logout = () => {
    clearTokens();
    router.replace("/login");
  };

  return {
    token,
    isAuthenticated: Boolean(token),
    logout,
  };
}
