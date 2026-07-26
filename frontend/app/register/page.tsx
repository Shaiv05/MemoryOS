"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { registerUser } from "@/services/auth";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const router = useRouter();
  const { isAuthenticated, isHydrated } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isHydrated && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isHydrated, isAuthenticated, router]);

  const getRegistrationError = (err: unknown) => {
    const data = (
      err as {
        response?: {
          data?: {
            username?: string[];
            email?: string[];
            password?: string[];
          };
        };
      }
    )?.response?.data;

    return (
      data?.username?.[0] ||
      data?.email?.[0] ||
      data?.password?.[0] ||
      "Registration failed."
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await registerUser({ username, email, password });
      router.push("/login");
    } catch (err: unknown) {
      setError(getRegistrationError(err));
    } finally {
      setLoading(false);
    }
  };

  if (!isHydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black px-4 text-white">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-800 border-t-white" />
      </main>
    );
  }

  if (isAuthenticated) {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-950 p-8 shadow-2xl">
        <h1 className="text-3xl font-semibold">Register</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Create your AI Second Brain account.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="mb-2 block text-sm text-zinc-300">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 outline-none placeholder:text-zinc-600 focus:border-zinc-600"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-300">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 outline-none placeholder:text-zinc-600 focus:border-zinc-600"
              placeholder="Enter email"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 outline-none placeholder:text-zinc-600 focus:border-zinc-600"
              placeholder="Enter password"
            />
          </div>

          {error && (
            <p className="rounded-xl border border-red-900/50 bg-red-950 px-4 py-3 text-sm text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-white px-4 py-3 font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-sm text-zinc-400">
          Already have an account?{" "}
          <a href="/login" className="text-white underline underline-offset-4">
            Login
          </a>
        </p>
      </div>
    </main>
  );
}
