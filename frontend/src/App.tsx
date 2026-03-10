import { Routes, Route, Navigate } from "react-router-dom";
import { OverviewPage } from "./pages/OverviewPage";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <header className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">SEO 数据看板</h1>
        </header>
        <Routes>
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="*" element={<Navigate to="/overview" replace />} />
        </Routes>
      </div>
    </div>
  );
}

