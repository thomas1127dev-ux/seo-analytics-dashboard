import { NavLink, useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "../auth/AuthContext";
import { useTheme } from "../theme/ThemeContext";

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
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const isDark = theme === "dark";

  return (
    <div
      className={
        "min-h-screen transition-colors duration-300 " +
        (isDark
          ? "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50"
          : "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 text-slate-900")
      }
    >
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6">
        <header className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              多站点 SEO 数据看板
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              聚合 GA4 / GSC / Yandex 的跨站点流量与搜索表现
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-full border border-slate-600/60 bg-slate-900/40 px-3 py-1 text-[11px] text-slate-200 shadow-sm shadow-black/40 transition hover:border-emerald-400/70 hover:bg-slate-900/80"
            >
              {isDark ? "切换为浅色主题" : "切换为深色主题"}
            </button>
            {user && (
              <span className="hidden md:inline">
                已登录：{user.name}（{user.email}
                {user.is_admin ? "，管理员" : ""}）
              </span>
            )}
            <button
              type="button"
              onClick={() => {
                logout();
                navigate("/login", { replace: true });
              }}
              className="rounded-full border border-slate-700 px-3 py-1 text-[11px] text-slate-200 hover:border-emerald-400/70 hover:bg-slate-900/80"
            >
              退出登录
            </button>
          </div>
        </header>
        <nav className="mb-6 flex gap-2 rounded-full bg-slate-900/60 p-1 text-sm shadow-lg shadow-black/40 ring-1 ring-slate-800/80">
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) =>
                "relative flex-1 rounded-full px-3 py-1 text-center transition-all duration-200 " +
                (isActive
                  ? "bg-emerald-500/10 text-emerald-200 shadow-[0_0_20px_rgba(16,185,129,0.35)]"
                  : "text-slate-300 hover:bg-slate-800/80 hover:text-slate-50")
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 pb-6">{children}</main>
        <footer className="mt-auto pt-4 text-xs text-slate-500">
          SEO数据可视化平台仅供内部运营分析使用。
        </footer>
      </div>
    </div>
  );
}


