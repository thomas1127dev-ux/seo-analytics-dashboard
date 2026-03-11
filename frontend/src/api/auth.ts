import { apiClient } from "./client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: number;
  email: string;
  name: string;
  is_admin: boolean;
}

export async function loginWithPassword(email: string, password: string) {
  const form = new URLSearchParams();
  // 后端使用 OAuth2PasswordRequestForm，字段名为 username / password
  form.append("username", email);
  form.append("password", password);

  const res = await apiClient.post<LoginResponse>("/api/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  });
  return res.data;
}

export async function fetchCurrentUser() {
  const res = await apiClient.get<CurrentUser>("/api/auth/me");
  return res.data;
}

