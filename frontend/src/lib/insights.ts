import { apiClient } from "@/lib/api-client";
import type { InsightResponse } from "@/lib/api-client";

export async function generateInsights(datasetId: string): Promise<InsightResponse> {
  return apiClient.post<InsightResponse>("/api/v1/insights/" + datasetId, {});
}
