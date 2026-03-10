import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchContentPerformance } from "../api/content";
import { SmartSelect } from "../components/SmartSelect";
import { DateButton } from "../components/DateButton";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function ContentPerformancePage() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [startDate, setStartDate] = useState(() => {
    const today = new Date();
    const d = new Date(today);
    d.setDate(d.getDate() - (DEFAULT_DAYS - 1));
    return formatDate(d);
  });
  const [endDate, setEndDate] = useState(() => formatDate(new Date()));

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects
  });

  useEffect(() => {
    if (!projectId && projectsQuery.data && projectsQuery.data.length > 0) {
      setProjectId(projectsQuery.data[0].id);
    }
  }, [projectId, projectsQuery.data]);

  const contentQuery = useQuery({
    queryKey: ["content", projectId, startDate, endDate],
    queryFn: () =>
      fetchContentPerformance({
        projectId: projectId as number,
        startDate,
        endDate,
        limit: 20
      }),
    enabled: projectId != null
  });

  const projects = projectsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <SmartSelect
          label="站点"
          value={projectId}
          options={projects.map((p) => ({
            value: p.id,
            label: `${p.name} (${p.domain})`
          }))}
          onChange={(val) => setProjectId(Number(val))}
        />
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300">
          <DateButton
            label="起"
            value={startDate}
            max={endDate}
            onChange={setStartDate}
          />
          <span className="text-slate-500">～</span>
          <DateButton
            label="止"
            value={endDate}
            min={startDate}
            onChange={setEndDate}
          />
          <button
            className="ml-2 rounded-full border border-slate-700 px-3 py-1 text-[11px] text-slate-200 hover:border-emerald-400/70 hover:bg-slate-900/80"
            type="button"
            onClick={() => {
              const today = new Date();
              const end = formatDate(today);
              const startDateObj = new Date(today);
              startDateObj.setDate(startDateObj.getDate() - (DEFAULT_DAYS - 1));
              const start = formatDate(startDateObj);
              setStartDate(start);
              setEndDate(end);
            }}
          >
            最近 7 天
          </button>
        </div>
      </div>

      {contentQuery.isLoading && (
        <div className="glass-card flex items-center justify-center py-10 text-sm text-slate-300">
          正在加载内容表现数据…
        </div>
      )}
      {contentQuery.isError && (
        <div className="text-red-400 text-sm">内容表现数据加载失败。</div>
      )}

      {contentQuery.data && (
        <>
          <div className="glass-card p-4">
            <div className="section-title">
              <span className="section-title-dot" />
              <span>Top 页面 PV 排行</span>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={contentQuery.data.pages.map((p) => ({
                    name: p.page_path.length > 24 ? p.page_path.slice(0, 24) + "…" : p.page_path,
                    page_views: p.page_views
                  }))}
                  layout="vertical"
                  margin={{ left: 80 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis
                    dataKey="name"
                    type="category"
                    stroke="#64748b"
                    width={120}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#020617",
                      borderColor: "#1e293b",
                      borderRadius: 8
                    }}
                  />
                  <Bar dataKey="page_views" fill="#22c55e" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card mt-4 overflow-hidden">
            <table className="w-full border-collapse text-sm">
              <thead className="text-slate-400">
                <tr>
                  <th className="border-b border-slate-800 py-1 text-left">
                    页面路径
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    PV
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    平均参与时长(s)
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    跳出率
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    7 天增长量
                  </th>
                </tr>
              </thead>
              <tbody>
                {contentQuery.data.pages.map((p) => (
                  <tr key={p.page_path} className="border-b border-slate-900">
                    <td className="py-1 max-w-xs truncate" title={p.page_path}>
                      {p.page_path}
                    </td>
                    <td className="py-1 text-right">
                      {Math.round(p.page_views).toLocaleString("zh-CN")}
                    </td>
                    <td className="py-1 text-right">
                      {p.avg_engagement_time.toFixed(1)}
                    </td>
                    <td className="py-1 text-right">
                      {(p.bounce_rate * 100).toFixed(1)}%
                    </td>
                    <td
                      className={
                        "py-1 text-right " +
                        (p.growth_7d > 0
                          ? "text-emerald-400"
                          : p.growth_7d < 0
                          ? "text-red-400"
                          : "text-slate-300")
                      }
                    >
                      {p.growth_7d > 0 ? "+" : ""}
                      {Math.round(p.growth_7d).toLocaleString("zh-CN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

