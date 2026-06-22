"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { apiClient } from "@/lib/api-client";
import type { UserResponse, DashboardSummary } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const u = await getCurrentUser();
        setUser(u);
        const s = await apiClient.get<DashboardSummary>("/api/v1/dashboard/summary");
        setSummary(s);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
        } else {
          setError(err instanceof ApiError ? err.message : "Failed to load dashboard.");
        }
      }
    }
    load();
  }, [router]);

  function handleLogout() {
    logout();
    router.push("/login");
  }

  if (error) return <p className="text-red-400 p-8">{error}</p>;
  if (!user) return <p className="text-zinc-500 p-8">Loading...</p>;

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-semibold">Welcome back, {user.full_name || user.email}</h1>
            <p className="text-zinc-500 text-sm">Plan: {user.plan}</p>
          </div>
        </div>

        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
            {[
              { label: "Total Datasets", value: summary.total_datasets },
              { label: "Analyzed", value: summary.ready_datasets },
              { label: "Chat Sessions", value: summary.chat_sessions },
              { label: "Forecast Reports", value: summary.forecast_reports },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 hover:border-zinc-700 transition-colors"
              >
                <p className="text-zinc-500 text-sm">{stat.label}</p>
                <p className="text-3xl font-semibold">{stat.value}</p>
              </motion.div>
            ))}
          </div>
        )}

        <div className="flex gap-3 mb-10">
          <button
            onClick={() => router.push("/dashboard/datasets")}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm hover:bg-blue-500"
          >
            Go to Datasets
          </button>
        </div>

        {summary && summary.recent_activity.length > 0 && (
          <div>
            <h2 className="text-lg font-medium mb-3">Recent Activity</h2>
            <div className="rounded-lg border border-zinc-800 overflow-hidden">
              {summary.recent_activity.map((item) => (
                <button
                  key={item.dataset_id}
                  onClick={() => router.push("/dashboard/datasets/" + item.dataset_id)}
                  className="w-full flex justify-between px-4 py-3 border-b border-zinc-800 last:border-b-0 hover:bg-zinc-900 text-left"
                >
                  <span>{item.name}</span>
                  <span className="text-zinc-500 text-sm">{item.status}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {summary && summary.recent_activity.length === 0 && (
          <p className="text-zinc-500 text-center py-8">No datasets yet. Upload your first one to get started.</p>
        )}
      </div>
    </main>
  );
}