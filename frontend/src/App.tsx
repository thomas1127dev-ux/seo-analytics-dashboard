import { Routes, Route, Navigate } from "react-router-dom";
import { OverviewPage } from "./pages/OverviewPage";
import { TrafficSourcesPage } from "./pages/TrafficSourcesPage";
import { ContentPerformancePage } from "./pages/ContentPerformancePage";
import { GoogleSEOPage } from "./pages/GoogleSEOPage";
import { YandexSEOPage } from "./pages/YandexSEOPage";
import { LoginPage } from "./pages/LoginPage";
import { Layout } from "./components/Layout";
import { useAuth } from "./auth/AuthContext";

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { user, initializing } = useAuth();

  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-slate-300">
        正在加载用户信息…
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <Layout>
            <Routes>
              <Route
                path="/overview"
                element={
                  <ProtectedRoute>
                    <OverviewPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/traffic"
                element={
                  <ProtectedRoute>
                    <TrafficSourcesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/content"
                element={
                  <ProtectedRoute>
                    <ContentPerformancePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/google-seo"
                element={
                  <ProtectedRoute>
                    <GoogleSEOPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/yandex-seo"
                element={
                  <ProtectedRoute>
                    <YandexSEOPage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  );
}


