"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  subscribeTokenChanges,
} from "@/lib/token-storage";
import { logoutUser } from "@/services/auth";

type UseAuthOptions = {
  required?: boolean;
};

export function useAuth(options: UseAuthOptions = {}) {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    let active = true;

    Promise.resolve().then(() => {
      if (!active) return;
      setToken(getAccessToken());
      setIsHydrated(true);
    });

    const unsubscribe = subscribeTokenChanges(() => {
      setToken(getAccessToken());
    });

    return () => {
      active = false;
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (isHydrated && options.required && !token) {
      router.replace("/login");
    }
  }, [isHydrated, options.required, token, router]);

  const logout = async () => {
    const refresh = getRefreshToken();
    if (refresh) {
      try {
        await logoutUser(refresh);
      } catch (err) {
        console.error("Backend logout failed:", err);
      }
    }
    clearTokens();
    router.replace("/login");
  };

  return {
    token,
    isAuthenticated: Boolean(token),
    isHydrated,
    logout,
  };
}
