"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser } from "@/services/auth";
import { setTokens } from "@/lib/token-storage";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getLoginError = (err: unknown) => {
    const response = (err as { response?: { data?: { detail?: string } } })?.response;
    return (
      response?.data?.detail ||
      "Login failed. Check your username and password."
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await loginUser({ username, password });
      setTokens(data.access, data.refresh);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(getLoginError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-950 p-8 shadow-2xl">
        <h1 className="text-3xl font-semibold">Login</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Access your AI Second Brain.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="mb-2 block text-sm text-zinc-300">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 outline-none ring-0 placeholder:text-zinc-600 focus:border-zinc-600"
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm text-zinc-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 outline-none ring-0 placeholder:text-zinc-600 focus:border-zinc-600"
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
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="mt-6 text-sm text-zinc-400">
          No account?{" "}
          <a href="/register" className="text-white underline underline-offset-4">
            Register
          </a>
        </p>
      </div>
    </main>
  );
}
