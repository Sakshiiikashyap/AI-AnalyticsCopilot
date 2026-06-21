"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getDataset, previewDataset, getDatasetProfile } from "@/lib/datasets";
import type { DatasetResponse, DatasetPreviewResponse, DatasetProfileResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";

export default function DatasetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [dataset, setDataset] = useState<DatasetResponse | null>(null);
  const [preview, setPreview] = useState<DatasetPreviewResponse | null>(null);
  const [profile, setProfile] = useState<DatasetProfileResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const ds = await getDataset(datasetId);
        setDataset(ds);
        if (ds.status === "ready") {
          const prev = await previewDataset(datasetId);
          setPreview(prev);
          try {
            const prof = await getDatasetProfile(datasetId);
            setProfile(prof);
          } catch (profileErr) {
            console.log("Profile not available yet:", profileErr);
          }
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
        } else {
          setError(err instanceof ApiError ? err.message : "Failed to load dataset.");
        }
      }
    }
    load();
  }, [datasetId, router]);

  if (error) return <p className="text-red-400 p-8">{error}</p>;
  if (!dataset) return <p className="text-zinc-500 p-8">Loading...</p>;

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-5xl mx-auto">
        <button onClick={() => router.push("/dashboard/datasets")} className="text-zinc-400 hover:text-white mb-4">
          Back to datasets
        </button>

        <button
          onClick={() => router.push("/dashboard/datasets/" + datasetId + "/chat")}
          className="ml-3 rounded-md bg-blue-600 px-3 py-1 text-sm hover:bg-blue-500"
        >
          Chat with this dataset
        </button>

        <h1 className="text-3xl font-semibold mb-2">{dataset.name}</h1>
        <p className="text-zinc-500 mb-6">
          {dataset.row_count} rows, {dataset.column_count} columns, status: {dataset.status}
        </p>

        {!profile && dataset.status === "ready" && (
          <div className="rounded-lg border border-yellow-800 bg-yellow-950 p-4 mb-6 text-yellow-300 text-sm">
            No profile found for this dataset. It was likely uploaded before profiling was added.
            Delete it and re-upload to generate a profile.
          </div>
        )}

        {profile && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
              <p className="text-zinc-500 text-sm">Duplicate Rows</p>
              <p className="text-2xl font-semibold">{profile.duplicates_count}</p>
            </div>
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
              <p className="text-zinc-500 text-sm">Missing Cells</p>
              <p className="text-2xl font-semibold">{profile.missing_values.total_missing_cells}</p>
            </div>
            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
              <p className="text-zinc-500 text-sm">Complete Rows</p>
              <p className="text-2xl font-semibold">{profile.missing_values.complete_rows}</p>
            </div>
          </div>
        )}

        {profile && profile.missing_values.columns_with_missing.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-medium mb-3">Missing Values by Column</h2>
            <div className="rounded-lg border border-zinc-800 overflow-hidden">
              {profile.missing_values.columns_with_missing.map((col) => (
                <div key={col.column} className="flex justify-between px-4 py-2 border-b border-zinc-800 last:border-b-0">
                  <span>{col.column}</span>
                  <span className="text-zinc-400">{col.missing_count} ({col.missing_percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile && profile.outliers.columns.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-medium mb-3">Outliers Detected (IQR method)</h2>
            <div className="rounded-lg border border-zinc-800 overflow-hidden">
              {profile.outliers.columns.map((col) => (
                <div key={col.column} className="flex justify-between px-4 py-2 border-b border-zinc-800 last:border-b-0">
                  <span>{col.column}</span>
                  <span className="text-zinc-400">{col.outlier_count} outliers ({col.outlier_percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {profile && profile.correlation.available && profile.correlation.strong_pairs.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-medium mb-3">Strong Correlations</h2>
            <div className="rounded-lg border border-zinc-800 overflow-hidden">
              {profile.correlation.strong_pairs.map((pair, i) => (
                <div key={i} className="flex justify-between px-4 py-2 border-b border-zinc-800 last:border-b-0">
                  <span>{pair.column_a} vs {pair.column_b}</span>
                  <span className={pair.correlation > 0 ? "text-green-400" : "text-red-400"}>
                    {pair.correlation}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {dataset.schema_json && (
          <div className="mb-8">
            <h2 className="text-lg font-medium mb-3">Schema</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {dataset.schema_json.columns.map((col) => (
                <div key={col.name} className="rounded-lg border border-zinc-800 bg-zinc-900 p-3">
                  <p className="font-medium text-sm truncate">{col.name}</p>
                  <p className="text-xs text-zinc-500">{col.semantic_type}</p>
                  <p className="text-xs text-zinc-600">{col.null_count} nulls</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {preview && (
          <div>
            <h2 className="text-lg font-medium mb-3">Preview (first 50 rows)</h2>
            <div className="overflow-x-auto rounded-lg border border-zinc-800">
              <table className="w-full text-sm">
                <thead className="bg-zinc-900">
                  <tr>
                    {preview.columns.map((col) => (
                      <th key={col} className="px-3 py-2 text-left font-medium text-zinc-300 whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((row, i) => (
                    <tr key={i} className="border-t border-zinc-800">
                      {preview.columns.map((col) => (
                        <td key={col} className="px-3 py-2 whitespace-nowrap text-zinc-400">
                          {row[col] === null ? "-" : String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}