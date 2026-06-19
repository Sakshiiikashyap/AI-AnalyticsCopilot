"use client";

import { useEffect, useState } from "react";
import { apiClient, HealthResponse, ApiError } from "@/lib/api-client";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<HealthResponse>("/health")
      .then(setHealth)
      .catch((err: ApiError) => setError(err.message));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white">
      <h1 className="text-3xl font-semibold mb-4">AI Analytics Copilot</h1>
      <p className="text-zinc-400 mb-6">Backend connection status:</p>

      {error && <p className="text-red-400">❌ {error}</p>}

      {health && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-6 py-4">
          <p>
            Status: <span className="text-green-400">{health.status}</span>
          </p>
          <p>
            Environment: <span className="text-blue-400">{health.environment}</span>
          </p>
        </div>
      )}

      {!health && !error && <p className="text-zinc-500">Connecting...</p>}
    </main>
  );
}