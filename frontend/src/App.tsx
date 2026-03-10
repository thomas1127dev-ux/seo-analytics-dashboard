import { Routes, Route, Navigate } from "react-router-dom";
import { OverviewPage } from "./pages/OverviewPage";
import { TrafficSourcesPage } from "./pages/TrafficSourcesPage";
import { ContentPerformancePage } from "./pages/ContentPerformancePage";
import { GoogleSEOPage } from "./pages/GoogleSEOPage";
import { YandexSEOPage } from "./pages/YandexSEOPage";
import { Layout } from "./components/Layout";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/traffic" element={<TrafficSourcesPage />} />
        <Route path="/content" element={<ContentPerformancePage />} />
        <Route path="/google-seo" element={<GoogleSEOPage />} />
        <Route path="/yandex-seo" element={<YandexSEOPage />} />
        <Route path="*" element={<Navigate to="/overview" replace />} />
      </Routes>
    </Layout>
  );
}

