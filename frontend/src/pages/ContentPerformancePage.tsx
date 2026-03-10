import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchContentPerformance } from "../api/content";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function ContentPerformancePage() {
  const [projectId, setProjectId] = useState<number | null>(null);

  const today = useMemo(() => new Date(), []);
  const startDate = useMemo(() => {
    const d = new Date(today);
    d.setDate(d.getDate() - (DEFAULT_DAYS - 1));
    return formatDate(d);
  }, [today]);
  const endDate = useMemo(() => formatDate(today), [today]);

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
      <div className="flex flex-wrap items-center gap-4">
        <select
          className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm"
          value={projectId ?? ""}
          onChange={(e) => setProjectId(Number(e.target.value))}
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.domain})
            </option>
          ))}
        </select>
        <div className="text-sm text-slate-300">
          最近 {DEFAULT_DAYS} 天内容表现（{startDate} ～ {endDate}）
        </div>
      </div>

      {contentQuery.isLoading && <div>加载中...</div>}
      {contentQuery.isError && (
        <div className="text-red-400 text-sm">内容表现数据加载失败。</div>
      )}

      {contentQuery.data && (
        <div>
          <table className="w-full text-sm border-collapse">
            <thead className="text-slate-400">
              <tr>
                <th className="border-b border-slate-800 py-1 text-left">
                  页面路径
                </th>
                <th className="border-b border-slate-800 py-1 text-right">PV</th>
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
      )}
    </div>
  );
}

