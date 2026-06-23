"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { runForecast } from "@/lib/forecast";
import type { ForecastResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function ForecastPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [result, setResult] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const res = await runForecast(datasetId, 30);
      setResult(res);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else {
        setError(err instanceof ApiError ? err.message : "Forecast failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  const chartData = result
    ? [
        ...result.history.map((h) => ({ date: h.date, actual: h.value })),
        ...result.forecast.map((f) => ({
          date: f.date,
          predicted: f.value,
          lower_bound: f.lower_bound,
          upper_bound: f.upper_bound,
        })),
      ]
    : [];

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-5xl mx-auto">
        <button
          onClick={() => router.push("/dashboard/datasets/" + datasetId)}
          className="text-zinc-400 hover:text-white mb-4 text-left"
        >
          Back to dataset
        </button>

        <h1 className="text-2xl font-semibold mb-4">Forecast</h1>

        {!result && (
          <button
            onClick={handleRun}
            disabled={loading}
            className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Training model and forecasting..." : "Run Forecast (next 30 periods)"}
          </button>
        )}

        {error && <p className="text-red-400 text-sm mt-4">{error}</p>}

        {result && (
          <div>
            <p className="text-zinc-500 text-sm mb-1">
              Forecasting {result.metric_column} using {result.date_column} ({result.frequency})
            </p>
            <p className="text-zinc-600 text-xs mb-6">{result.method}</p>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4" style={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="date" stroke="#71717a" fontSize={11} />
                  <YAxis stroke="#71717a" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181b", border: "1px solid #27272a", borderRadius: 8 }}
                  />
                  <Legend />
                  <Area dataKey="upper_bound" stroke="none" fill="#3b82f6" fillOpacity={0.1} name="Confidence band" />
                  <Area dataKey="lower_bound" stroke="none" fill="#18181b" fillOpacity={1} name="" legendType="none" />
                  <Line dataKey="actual" stroke="#a1a1aa" dot={false} name="Historical" strokeWidth={2} />
                  <Line dataKey="predicted" stroke="#3b82f6" dot={false} name="Forecast" strokeWidth={2} strokeDasharray="5 5" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <button
              onClick={handleRun}
              disabled={loading}
              className="mt-4 rounded-md bg-zinc-800 px-4 py-2 text-sm hover:bg-zinc-700 disabled:opacity-50"
            >
              {loading ? "Re-running..." : "Re-run Forecast"}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}