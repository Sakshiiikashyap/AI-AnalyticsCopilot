"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getDataset, previewDataset } from "@/lib/datasets";
import { DatasetResponse, DatasetPreviewResponse, ApiError } from "@/lib/api-client";

export default function DatasetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [dataset, setDataset] = useState<DatasetResponse | null>(null);
  const [preview, setPreview] = useState<DatasetPreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const ds = await getDataset(datasetId);
        setDataset(ds);
        if (ds.status === "ready") {
          const prev = await previewDataset(datasetId);
          setPreview(prev);
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
          ← Back to datasets
        </button>

        <h1 className="text-3xl font-semibold mb-2">{dataset.name}</h1>
        <p className="text-zinc-500 mb-6">
          {dataset.row_count} rows · {dataset.column_count} columns · status: {dataset.status}
        </p>

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
            <h2 className="text-lg font-medium mb-3">Preview (first {preview.rows.length} rows)</h2>
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
                          {row[col] === null ? "—" : String(row[col])}
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