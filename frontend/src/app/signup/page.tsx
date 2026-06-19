"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signup } from "@/lib/auth";
import { ApiError } from "@/lib/api-client";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signup(email, password, fullName);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-white px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-xl border border-zinc-800 bg-zinc-900 p-8 space-y-4"
      >
        <h1 className="text-2xl font-semibold mb-2">Create your account</h1>

        <input
          type="text"
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full rounded-md bg-zinc-800 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md bg-zinc-800 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder="Password (min 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md bg-zinc-800 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        />

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-600 py-2 font-medium hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>

        <p className="text-sm text-zinc-400 text-center">
          Already have an account?{" "}
          <a href="/login" className="text-blue-400 hover:underline">
            Log in
          </a>
        </p>
      </form>
    </main>
  );
}