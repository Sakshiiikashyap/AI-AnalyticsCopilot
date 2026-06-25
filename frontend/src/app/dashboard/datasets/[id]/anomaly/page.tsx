"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { runAnomalyDetection } from "@/lib/anomaly";
import type { AnomalyResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis } from "recharts";

export default function AnomalyPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [method, setMethod] = useState("isolation_forest");
  const [contamination, setContamination] = useState(0.05);
  const [result, setResult] = useState<AnomalyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const res = await runAnomalyDetection(datasetId, method, contamination);
      setResult(res);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else {
        setError(err instanceof ApiError ? err.message : "Anomaly detection failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  const scatterData = result
    ? result.anomalies.map((a) => ({
        x: a.row_index,
        y: a.anomaly_score,
        score: a.anomaly_score,
      }))
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

        <h1 className="text-2xl font-semibold mb-6">Anomaly Detection</h1>

        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-zinc-500 text-sm mb-1">Method</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full rounded-md bg-zinc-800 border border-zinc-700 px-3 py-2 text-sm"
            >
              <option value="isolation_forest">Isolation Forest</option>
              <option value="dbscan">DBSCAN</option>
            </select>
          </div>

          <div>
            <label className="block text-zinc-500 text-sm mb-1">
              Sensitivity (expected anomaly fraction): {(contamination * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min={0.01}
              max={0.2}
              step={0.01}
              value={contamination}
              onChange={(e) => setContamination(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50 mb-6"
        >
          {loading ? "Running detection..." : "Run Anomaly Detection"}
        </button>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {result && (
          <div>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
                <p className="text-zinc-500 text-sm">Anomalies Found</p>
                <p className="text-2xl font-semibold">{result.anomaly_count}</p>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
                <p className="text-zinc-500 text-sm">Total Rows</p>
                <p className="text-2xl font-semibold">{result.total_rows}</p>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
                <p className="text-zinc-500 text-sm">% Flagged</p>
                <p className="text-2xl font-semibold">
                  {((result.anomaly_count / result.total_rows) * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            <p className="text-zinc-500 text-xs mb-3">
              Columns used: {result.columns_used.join(", ")}
            </p>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 mb-6" style={{ height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis type="number" dataKey="x" name="Row Index" stroke="#71717a" fontSize={11} />
                  <YAxis type="number" dataKey="y" name="Anomaly Score" stroke="#71717a" fontSize={11} />
                  <ZAxis range={[40, 40]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#18181b", border: "1px solid #27272a", borderRadius: 8 }}
                    cursor={{ strokeDasharray: "3 3" }}
                  />
                  <Scatter data={scatterData}>
                    {scatterData.map((entry, index) => (
                      <Cell key={index} fill={entry.score > 0.7 ? "#ef4444" : "#f59e0b"} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            <h2 className="text-lg font-medium mb-3">Top Flagged Rows</h2>
            <div className="space-y-2">
              {result.anomalies.slice(0, 10).map((a) => (
                <div key={a.row_index} className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-sm">
                  <div className="flex justify-between mb-2">
                    <span className="text-zinc-400">Row {a.row_index}</span>
                    <span className={a.anomaly_score > 0.7 ? "text-red-400" : "text-yellow-400"}>
                      Score: {a.anomaly_score}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-zinc-500 text-xs">
                    {Object.entries(a.row_data).map(([key, value]) => (
                      <span key={key}>
                        {key}: <span className="text-zinc-300">{String(value)}</span>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}