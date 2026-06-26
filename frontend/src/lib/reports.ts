import { apiClient, downloadFile } from "@/lib/api-client";
import type { ReportResponse } from "@/lib/api-client";

export async function generateReport(datasetId: string): Promise<ReportResponse> {
  return apiClient.post<ReportResponse>("/api/v1/reports/" + datasetId + "/generate", {});
}

export async function downloadReport(reportId: string): Promise<void> {
  return downloadFile("/api/v1/reports/" + reportId + "/download", "report-" + reportId + ".pdf");
}
