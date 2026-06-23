import { apiClient } from "@/lib/api-client";
import type { ForecastResponse } from "@/lib/api-client";

export async function runForecast(
  datasetId: string,
  periods: number,
  dateColumn?: string,
  metricColumn?: string
): Promise<ForecastResponse> {
  return apiClient.post<ForecastResponse>("/api/v1/forecast/" + datasetId, {
    periods: periods,
    date_column: dateColumn || null,
    metric_column: metricColumn || null,
  });
}
