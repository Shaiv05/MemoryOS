"use client";

import { useAuth } from "@/hooks/useAuth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { token, isHydrated } = useAuth({ required: true });

  if (!isHydrated) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-black text-white">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-800 border-t-white" />
      </div>
    );
  }

  if (!token) {
    return null;
  }

  return <>{children}</>;
}
