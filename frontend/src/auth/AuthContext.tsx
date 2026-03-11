import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode
} from "react";
import { fetchCurrentUser, loginWithPassword, type CurrentUser } from "../api/auth";
import { setAuthToken } from "../api/client";

interface AuthContextValue {
  user: CurrentUser | null;
  token: string | null;
  initializing: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_STORAGE_KEY = "seo_dashboard_access_token";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [initializing, setInitializing] = useState(true);

  // 首次挂载时，从 localStorage 恢复 token 并尝试获取用户信息
  useEffect(() => {
    const stored = window.localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!stored) {
      setInitializing(false);
      return;
    }

    setAuthToken(stored);
    setToken(stored);

    fetchCurrentUser()
      .then((u) => {
        setUser(u);
      })
      .catch(() => {
        // token 失效则清理本地状态
        window.localStorage.removeItem(TOKEN_STORAGE_KEY);
        setAuthToken(null);
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setInitializing(false);
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const loginRes = await loginWithPassword(email, password);
    const newToken = loginRes.access_token;

    setAuthToken(newToken);
    window.localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
    setToken(newToken);

    const me = await fetchCurrentUser();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }, []);

  const value: AuthContextValue = {
    user,
    token,
    initializing,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth 必须在 AuthProvider 内部使用");
  }
  return ctx;
}

