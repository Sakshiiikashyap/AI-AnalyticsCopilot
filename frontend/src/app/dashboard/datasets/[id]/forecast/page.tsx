"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { runForecast } from "@/lib/forecast";
import { getDataset } from "@/lib/datasets";
import type { ForecastResponse, DatasetResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function ForecastPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [dataset, setDataset] = useState<DatasetResponse | null>(null);
  const [dateColumn, setDateColumn] = useState<string>("");
  const [metricColumn, setMetricColumn] = useState<string>("");
  const [periods, setPeriods] = useState<number>(30);

  const [result, setResult] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const ds = await getDataset(datasetId);
        setDataset(ds);

        const dateCols = (ds.schema_json?.columns || []).filter((c) => c.semantic_type === "datetime");
        const numericCols = (ds.schema_json?.columns || []).filter(
          (c) => c.semantic_type === "integer" || c.semantic_type === "float"
        );

        if (dateCols.length > 0) setDateColumn(dateCols[0].name);
        if (numericCols.length > 0) setMetricColumn(numericCols[0].name);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
        }
      }
    }
    load();
  }, [datasetId, router]);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const res = await runForecast(datasetId, periods, dateColumn, metricColumn);
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

  const dateColumnOptions = dataset?.schema_json?.columns.filter((c) => c.semantic_type === "datetime") || [];
  const metricColumnOptions =
    dataset?.schema_json?.columns.filter((c) => c.semantic_type === "integer" || c.semantic_type === "float") || [];

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

        <h1 className="text-2xl font-semibold mb-6">Forecast</h1>

        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-zinc-500 text-sm mb-1">Date column</label>
            <select
              value={dateColumn}
              onChange={(e) => setDateColumn(e.target.value)}
              className="w-full rounded-md bg-zinc-800 border border-zinc-700 px-3 py-2 text-sm"
            >
              {dateColumnOptions.length === 0 && <option value="">No date column detected</option>}
              {dateColumnOptions.map((c) => (
                <option key={c.name} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-zinc-500 text-sm mb-1">Metric to forecast</label>
            <select
              value={metricColumn}
              onChange={(e) => setMetricColumn(e.target.value)}
              className="w-full rounded-md bg-zinc-800 border border-zinc-700 px-3 py-2 text-sm"
            >
              {metricColumnOptions.length === 0 && <option value="">No numeric column found</option>}
              {metricColumnOptions.map((c) => (
                <option key={c.name} value={c.name}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-zinc-500 text-sm mb-1">Periods ahead</label>
            <input
              type="number"
              min={1}
              max={365}
              value={periods}
              onChange={(e) => setPeriods(Number(e.target.value))}
              className="w-full rounded-md bg-zinc-800 border border-zinc-700 px-3 py-2 text-sm"
            />
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={loading || !dateColumn || !metricColumn}
          className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50 mb-6"
        >
          {loading ? "Training model and forecasting..." : "Run Forecast"}
        </button>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {result && (
          <div>
            <p className="text-zinc-500 text-sm mb-1">
              Forecasting {result.metric_column} using {result.date_column} ({result.frequency})
            </p>
            <p className="text-zinc-600 text-xs mb-4">{result.method}</p>

            {result.warning && (
              <div className="rounded-lg border border-yellow-800 bg-yellow-950 p-3 mb-4 text-yellow-300 text-sm">
                {result.warning}
              </div>
            )}

            {result.backtest && (
              <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 mb-6 grid grid-cols-3 gap-4">
                <div>
                  <p className="text-zinc-500 text-xs mb-1">Backtest MAE</p>
                  <p className="text-xl font-semibold">{result.backtest.mae}</p>
                  {result.backtest.mae_percentage_of_mean !== null && (
                    <p className="text-zinc-600 text-xs">{result.backtest.mae_percentage_of_mean}% of mean value</p>
                  )}
                </div>
                <div>
                  <p className="text-zinc-500 text-xs mb-1">Backtest RMSE</p>
                  <p className="text-xl font-semibold">{result.backtest.rmse}</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-xs mb-1">Validated on</p>
                  <p className="text-xl font-semibold">{result.backtest.holdout_periods} periods</p>
                </div>
              </div>
            )}

            {!result.backtest && (
              <p className="text-zinc-600 text-xs mb-6">
                Not enough historical data to compute a backtest accuracy estimate.
              </p>
            )}

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
          </div>
        )}
      </div>
    </main>
  );
}