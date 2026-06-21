import { apiClient } from "@/lib/api-client";
import type { ChatSessionResponse, ChatMessageResponse } from "@/lib/api-client";

export async function createChatSession(datasetId: string): Promise<ChatSessionResponse> {
  return apiClient.post<ChatSessionResponse>("/api/v1/chat/sessions", { dataset_id: datasetId });
}

export async function listChatMessages(sessionId: string): Promise<ChatMessageResponse[]> {
  return apiClient.get<ChatMessageResponse[]>("/api/v1/chat/sessions/" + sessionId + "/messages");
}

export async function sendChatMessage(sessionId: string, content: string): Promise<ChatMessageResponse> {
  return apiClient.post<ChatMessageResponse>("/api/v1/chat/sessions/" + sessionId + "/messages", { content });
}
