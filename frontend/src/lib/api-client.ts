const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function setToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function clearToken() {
  localStorage.removeItem("access_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(body.detail || "Request failed", res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export async function uploadFile<T>(path: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  const token = getToken();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new ApiError(body.detail || "Upload failed", res.status);
  }

  return res.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: "POST", body: data ? JSON.stringify(data) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

export interface HealthResponse {
  status: string;
  environment: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  plan: string;
  created_at: string;
}

export interface DatasetColumn {
  name: string;
  dtype: string;
  semantic_type: string;
  null_count: number;
  unique_count: number;
  min?: number;
  max?: number;
  mean?: number;
}

export interface DatasetSchema {
  row_count: number;
  column_count: number;
  columns: DatasetColumn[];
}

export interface DatasetResponse {
  id: string;
  name: string;
  original_filename: string;
  file_type: string;
  row_count: number | null;
  column_count: number | null;
  schema_json: DatasetSchema | null;
  status: string;
  created_at: string;
}

export interface DatasetPreviewResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  total_rows: number;
}

export interface MissingValueColumn {
  column: string;
  missing_count: number;
  missing_percentage: number;
}

export interface MissingValuesSummary {
  total_missing_cells: number;
  columns_with_missing: MissingValueColumn[];
  complete_rows: number;
}

export interface CorrelationPair {
  column_a: string;
  column_b: string;
  correlation: number;
}

export interface CorrelationSummary {
  available: boolean;
  reason?: string;
  matrix: Record<string, Record<string, number | null>>;
  strong_pairs: CorrelationPair[];
}

export interface OutlierColumn {
  column: string;
  outlier_count: number;
  outlier_percentage: number;
  lower_bound: number | null;
  upper_bound: number | null;
}

export interface OutliersSummary {
  method: string;
  columns: OutlierColumn[];
}

export interface DatasetProfileResponse {
  dataset_id: string;
  summary: Record<string, unknown>;
  missing_values: MissingValuesSummary;
  duplicates_count: number;
  correlation: CorrelationSummary;
  outliers: OutliersSummary;
  generated_at: string;
}

export interface ChatSessionResponse {
  id: string;
  dataset_id: string;
  created_at: string;
}

export interface ChatMessageResponse {
  id: string;
  role: string;
  content: string;
  computed_context: Record<string, unknown> | null;
  created_at: string;
}