import { apiClient, uploadFile, DatasetResponse, DatasetPreviewResponse } from "@/lib/api-client";

export async function uploadDataset(file: File): Promise<DatasetResponse> {
  return uploadFile<DatasetResponse>("/api/v1/datasets/upload", file);
}

export async function listDatasets(): Promise<DatasetResponse[]> {
  return apiClient.get<DatasetResponse[]>("/api/v1/datasets");
}

export async function getDataset(id: string): Promise<DatasetResponse> {
  return apiClient.get<DatasetResponse>(`/api/v1/datasets/${id}`);
}

export async function previewDataset(id: string): Promise<DatasetPreviewResponse> {
  return apiClient.get<DatasetPreviewResponse>(`/api/v1/datasets/${id}/preview`);
}