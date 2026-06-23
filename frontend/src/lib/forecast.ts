import { apiClient } from "@/lib/api-client";
import type { ForecastResponse } from "@/lib/api-client";

export async function runForecast(datasetId: string, periods: number): Promise<ForecastResponse> {
  return apiClient.post<ForecastResponse>("/api/v1/forecast/" + datasetId, { periods: periods });
}
