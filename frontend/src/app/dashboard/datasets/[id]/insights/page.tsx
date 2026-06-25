"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { generateInsights } from "@/lib/insights";
import type { InsightResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";

export default function InsightsPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [result, setResult] = useState<InsightResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await generateInsights(datasetId);
      setResult(res);
      setCooldown(15);
      const interval = setInterval(() => {
        setCooldown((c) => {
          if (c <= 1) {
            clearInterval(interval);
            return 0;
          }
          return c - 1;
        });
      }, 1000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else if (err instanceof ApiError && err.status === 502) {
        setError("The AI service is busy right now (rate limit). Please wait a moment and try again.");
      } else {
        setError(err instanceof ApiError ? err.message : "Could not generate insights.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => router.push("/dashboard/datasets/" + datasetId)}
          className="text-zinc-400 hover:text-white mb-4 text-left"
        >
          Back to dataset
        </button>

        <h1 className="text-2xl font-semibold mb-6">AI Insight Summary</h1>

        <button
          onClick={handleGenerate}
          disabled={loading || cooldown > 0}
          className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50 mb-6"
        >
          {loading
            ? "Generating insights..."
            : cooldown > 0
            ? "Wait " + cooldown + "s before regenerating"
            : "Generate Insight Summary"}
        </button>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {result && (
          <div className="space-y-6">
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="text-sm font-medium text-zinc-500 mb-2">SUMMARY</h2>
              <p className="text-zinc-200">{result.summary}</p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="text-sm font-medium text-zinc-500 mb-3">KEY FINDINGS</h2>
              <ul className="space-y-2">
                {result.key_findings.map((item, i) => (
                  <li key={i} className="flex gap-2 text-sm text-zinc-300">
                    <span className="text-blue-400">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {result.risks.length > 0 && (
              <div className="rounded-lg border border-red-900 bg-red-950/30 p-5">
                <h2 className="text-sm font-medium text-red-400 mb-3">RISKS</h2>
                <ul className="space-y-2">
                  {result.risks.map((item, i) => (
                    <li key={i} className="flex gap-2 text-sm text-red-200">
                      <span>•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.opportunities.length > 0 && (
              <div className="rounded-lg border border-green-900 bg-green-950/30 p-5">
                <h2 className="text-sm font-medium text-green-400 mb-3">OPPORTUNITIES</h2>
                <ul className="space-y-2">
                  {result.opportunities.map((item, i) => (
                    <li key={i} className="flex gap-2 text-sm text-green-200">
                      <span>•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="rounded-lg border border-blue-900 bg-blue-950/30 p-5">
              <h2 className="text-sm font-medium text-blue-400 mb-3">RECOMMENDATIONS</h2>
              <ul className="space-y-2">
                {result.recommendations.map((item, i) => (
                  <li key={i} className="flex gap-2 text-sm text-blue-200">
                    <span>•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}