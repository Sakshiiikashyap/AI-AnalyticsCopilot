import { apiClient, setToken, clearToken, TokenResponse, UserResponse } from "@/lib/api-client";

export async function signup(email: string, password: string, fullName?: string) {
  const tokens = await apiClient.post<TokenResponse>("/api/v1/auth/signup", {
    email,
    password,
    full_name: fullName || null,
  });
  setToken(tokens.access_token);
  return tokens;
}

export async function login(email: string, password: string) {
  const tokens = await apiClient.post<TokenResponse>("/api/v1/auth/login", { email, password });
  setToken(tokens.access_token);
  return tokens;
}

export async function getCurrentUser(): Promise<UserResponse> {
  return apiClient.get<UserResponse>("/api/v1/auth/me");
}

export function logout() {
  clearToken();
}