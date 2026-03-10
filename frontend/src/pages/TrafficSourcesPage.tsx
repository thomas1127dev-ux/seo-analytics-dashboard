import { useMemo, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchTrafficSources } from "../api/traffic";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function TrafficSourcesPage() {
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

  const trafficQuery = useQuery({
    queryKey: ["traffic", projectId, startDate, endDate],
    queryFn: () =>
      fetchTrafficSources({
        projectId: projectId as number,
        startDate,
        endDate
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
          最近 {DEFAULT_DAYS} 天流量来源分布（{startDate} ～ {endDate}）
        </div>
      </div>

      {trafficQuery.isLoading && <div>加载中...</div>}
      {trafficQuery.isError && (
        <div className="text-red-400 text-sm">流量来源数据加载失败。</div>
      )}

      {trafficQuery.data && (
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-200">
              来源占比
            </h2>
            <table className="w-full text-sm border-collapse">
              <thead className="text-slate-400">
                <tr>
                  <th className="border-b border-slate-800 py-1 text-left">
                    渠道
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    会话
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    用户
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    PV
                  </th>
                  <th className="border-b border-slate-800 py-1 text-right">
                    占比
                  </th>
                </tr>
              </thead>
              <tbody>
                {trafficQuery.data.sources.map((s) => (
                  <tr key={s.channel} className="border-b border-slate-900">
                    <td className="py-1">{s.channel}</td>
                    <td className="py-1 text-right">
                      {Math.round(s.sessions).toLocaleString("zh-CN")}
                    </td>
                    <td className="py-1 text-right">
                      {Math.round(s.users).toLocaleString("zh-CN")}
                    </td>
                    <td className="py-1 text-right">
                      {Math.round(s.page_views).toLocaleString("zh-CN")}
                    </td>
                    <td className="py-1 text-right">
                      {(s.ratio * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-200">
              会话趋势（按渠道）
            </h2>
            <div className="text-xs text-slate-400">
              这里先用表格展示：日期 × 渠道 × 会话数，后续可替换为折线图。
            </div>
            <div className="mt-2 max-h-64 overflow-auto border border-slate-800 rounded">
              <table className="w-full text-xs border-collapse">
                <thead className="text-slate-400 sticky top-0 bg-slate-950">
                  <tr>
                    <th className="border-b border-slate-800 py-1 text-left">
                      日期
                    </th>
                    <th className="border-b border-slate-800 py-1 text-left">
                      渠道
                    </th>
                    <th className="border-b border-slate-800 py-1 text-right">
                      会话数
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {trafficQuery.data.trend_7d.map((p, idx) => (
                    <tr
                      key={`${p.date}-${p.channel}-${idx}`}
                      className="border-b border-slate-900"
                    >
                      <td className="py-1">{p.date}</td>
                      <td className="py-1">{p.channel}</td>
                      <td className="py-1 text-right">
                        {Math.round(p.sessions).toLocaleString("zh-CN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

