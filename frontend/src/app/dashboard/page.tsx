"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { UserResponse, ApiError } from "@/lib/api-client";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((err: ApiError) => {
        if (err.status === 401) {
          router.push("/login");
        } else {
          setError(err.message);
        }
      });
  }, [router]);

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white px-4">
      <h1 className="text-3xl font-semibold mb-6">Dashboard</h1>

      {error && <p className="text-red-400">{error}</p>}

      {user && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 space-y-2 w-full max-w-sm">
          <p>
            <span className="text-zinc-400">Email:</span> {user.email}
          </p>
          <p>
            <span className="text-zinc-400">Name:</span> {user.full_name || "—"}
          </p>
          <p>
            <span className="text-zinc-400">Plan:</span> {user.plan}
          </p>

          
            <a href="/dashboard/datasets"
            className="mt-4 block text-center rounded-md bg-blue-600 py-2 hover:bg-blue-500"
          >
            Go to Datasets →
          </a>

          <button
            onClick={handleLogout}
            className="mt-2 w-full rounded-md bg-zinc-800 py-2 hover:bg-zinc-700"
          >
            Log out
          </button>
        </div>
      )}

      {!user && !error && <p className="text-zinc-500">Loading...</p>}
    </main>
  );
}