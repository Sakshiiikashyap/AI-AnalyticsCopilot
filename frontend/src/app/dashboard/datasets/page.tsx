"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { uploadDataset, listDatasets } from "@/lib/datasets";
import { DatasetResponse, ApiError } from "@/lib/api-client";

export default function DatasetsPage() {
  const router = useRouter();
  const [datasets, setDatasets] = useState<DatasetResponse[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const data = await listDatasets();
      setDatasets(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      } else {
        setError(err instanceof ApiError ? err.message : "Failed to load datasets.");
      }
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    try {
      await uploadDataset(file);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      e.target.value = ""; // reset so the same file can be re-selected if needed
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-semibold mb-6">Your Datasets</h1>

        <label className="block border-2 border-dashed border-zinc-700 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 transition-colors mb-8">
          <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFileChange} disabled={uploading} />
          <p className="text-zinc-300">
            {uploading ? "Uploading and analyzing..." : "Click to upload a CSV or XLSX file"}
          </p>
          <p className="text-zinc-500 text-sm mt-1">Max 50MB</p>
        </label>

        {error && <p className="text-red-400 mb-4">{error}</p>}

        <div className="space-y-3">
          {datasets.map((ds) => (
            <button
              key={ds.id}
              onClick={() => router.push(`/dashboard/datasets/${ds.id}`)}
              className="w-full text-left rounded-lg border border-zinc-800 bg-zinc-900 p-4 hover:border-zinc-600 transition-colors flex justify-between items-center"
            >
              <div>
                <p className="font-medium">{ds.name}</p>
                <p className="text-sm text-zinc-500">
                  {ds.row_count ?? "—"} rows · {ds.column_count ?? "—"} columns · {ds.file_type.toUpperCase()}
                </p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  ds.status === "ready"
                    ? "bg-green-900 text-green-300"
                    : ds.status === "failed"
                    ? "bg-red-900 text-red-300"
                    : "bg-yellow-900 text-yellow-300"
                }`}
              >
                {ds.status}
              </span>
            </button>
          ))}

          {datasets.length === 0 && <p className="text-zinc-500 text-center py-8">No datasets uploaded yet.</p>}
        </div>
      </div>
    </main>
  );
}