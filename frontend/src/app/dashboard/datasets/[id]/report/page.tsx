"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { generateReport, downloadReport } from "@/lib/reports";
import { ApiError } from "@/lib/api-client";

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [reportId, setReportId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await generateReport(datasetId);
      setReportId(res.id);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else {
        setError(err instanceof ApiError ? err.message : "Could not generate report.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload() {
    if (!reportId) return;
    setDownloading(true);
    setError(null);
    try {
      await downloadReport(reportId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Download failed.");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => router.push("/dashboard/datasets/" + datasetId)}
          className="text-zinc-400 hover:text-white mb-4 text-left"
        >
          Back to dataset
        </button>

        <h1 className="text-2xl font-semibold mb-2">Executive Report</h1>
        <p className="text-zinc-500 text-sm mb-6">
          Generates a PDF combining your dataset's profile, anomaly detection, forecast, and AI
          insight summary, whichever have already been run.
        </p>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50 mb-4"
        >
          {loading ? "Generating PDF..." : "Generate Report"}
        </button>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {reportId && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
            <p className="text-zinc-300 mb-3">Report generated successfully.</p>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="rounded-md bg-green-700 px-4 py-2 hover:bg-green-600 disabled:opacity-50"
            >
              {downloading ? "Downloading..." : "Download PDF"}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}