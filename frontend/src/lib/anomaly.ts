import { apiClient } from "@/lib/api-client";
import type { AnomalyResponse } from "@/lib/api-client";

export async function runAnomalyDetection(
  datasetId: string,
  method: string,
  contamination: number
): Promise<AnomalyResponse> {
  return apiClient.post<AnomalyResponse>("/api/v1/anomaly/" + datasetId, {
    method: method,
    contamination: contamination,
  });
}
