import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

const tabs = [
  { path: "/overview", label: "总览" },
  { path: "/traffic", label: "流量来源" },
  { path: "/content", label: "内容表现" },
  { path: "/google-seo", label: "Google SEO" },
  { path: "/yandex-seo", label: "Yandex SEO" }
];

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <header className="mb-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">多站点 SEO 数据看板</h1>
        </header>
        <nav className="mb-6 flex gap-2 border-b border-slate-800 pb-2 text-sm">
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) =>
                "px-3 py-1 rounded-full border " +
                (isActive
                  ? "border-emerald-400 bg-emerald-500/10 text-emerald-200"
                  : "border-slate-700 text-slate-300 hover:border-slate-500")
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
        {children}
      </div>
    </div>
  );
}

