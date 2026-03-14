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

function SunIcon(props: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className={props.className}
    >
      <circle cx="12" cy="12" r="4.5" />
      <path d="M12 2.25v2.5M12 19.25v2.5M4.22 4.22l1.77 1.77M17.99 17.99l1.79 1.79M2.25 12h2.5M19.25 12h2.5M4.22 19.78l1.77-1.77M17.99 6.01l1.79-1.79" />
    </svg>
  );
}

function MoonIcon(props: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className={props.className}
    >
      <path d="M20.25 14.5A7.25 7.25 0 0 1 11 5.25 5.75 5.75 0 1 0 20.25 14.5Z" />
    </svg>
  );
}

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
            {/* 主题切换开关 */}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={isDark ? "切换为浅色主题" : "切换为深色主题"}
              className={
                "relative inline-flex h-6 w-12 items-center rounded-full border transition-colors shadow-sm " +
                (isDark
                  ? "border-slate-600/70 bg-slate-900/80 shadow-black/40"
                  : "border-slate-200 bg-white shadow-slate-900/5")
              }
            >
              <span className="pointer-events-none flex w-full items-center justify-between px-1.5">
                <SunIcon
                  className={
                    "h-4 w-4 transition-colors " +
                    (isDark ? "fill-slate-400" : "fill-amber-500")
                  }
                />
                <MoonIcon
                  className={
                    "h-4 w-4 transition-colors " +
                    (isDark ? "fill-sky-400" : "fill-slate-400")
                  }
                />
              </span>
              {/* 滑块 */}
              <span
                className={
                  "pointer-events-none absolute h-4 w-4 transform rounded-full bg-emerald-400 shadow transition-transform duration-200 " +
                  (isDark ? "translate-x-1" : "translate-x-6")
                }
              />
            </button>
            {user && (
              <span
                className={
                  "hidden md:inline " +
                  (isDark ? "text-slate-400" : "text-slate-500")
                }
              >
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
              className={
                "rounded-full px-3 py-1 text-[11px] transition " +
                (isDark
                  ? "border border-slate-700 text-slate-200 hover:border-emerald-400/70 hover:bg-slate-900/80"
                  : "border border-slate-300 bg-white/90 text-slate-800 shadow-sm shadow-slate-900/5 hover:border-emerald-400/70 hover:bg-emerald-50/80")
              }
            >
              退出登录
            </button>
          </div>
        </header>
        <nav
          className={
            "mb-6 flex gap-2 rounded-full p-1 text-sm shadow-lg ring-1 transition-colors " +
            (isDark
              ? "bg-slate-900/60 shadow-black/40 ring-slate-800/80"
              : "bg-white/90 shadow-slate-900/5 ring-slate-200")
          }
        >
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) => {
                const base =
                  "relative flex-1 rounded-full px-3 py-1 text-center text-xs font-medium transition-all duration-200 ";
                if (isDark) {
                  return (
                    base +
                    (isActive
                      ? "bg-emerald-500/10 text-emerald-200 shadow-[0_0_16px_rgba(16,185,129,0.35)]"
                      : "text-slate-300 hover:bg-slate-800/80 hover:text-slate-50")
                  );
                }
                return (
                  base +
                  (isActive
                    ? "bg-emerald-500/10 text-emerald-700 shadow-[0_0_12px_rgba(16,185,129,0.25)]"
                    : "text-slate-500 hover:bg-slate-100 hover:text-slate-900")
                );
              }}
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


