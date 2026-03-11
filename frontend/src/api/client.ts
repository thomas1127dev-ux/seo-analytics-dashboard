import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:4000";

export const apiClient = axios.create({
  baseURL,
  timeout: 15000
});

/**
 * 设置全局认证 Token，供后续请求使用。
 */
export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
}

/**
 * 统一处理 401/403 响应，方便在外层做登出与跳转。
 * 实际的登出逻辑在 AuthContext 中处理，这里仅抛出错误。
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // 在需要时可在这里触发全局事件，当前仅让调用方感知错误
    }
    return Promise.reject(error);
  }
);


