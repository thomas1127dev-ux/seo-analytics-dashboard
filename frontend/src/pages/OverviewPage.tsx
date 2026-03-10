import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchOverview } from "../api/overview";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function OverviewPage() {
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

  const overviewQuery = useQuery({
    queryKey: ["overview", projectId, startDate, endDate],
    queryFn: () =>
      fetchOverview({
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
          日期范围：{startDate} ～ {endDate}
        </div>
      </div>

      {overviewQuery.isLoading && <div>加载中...</div>}
      {overviewQuery.isError && (
        <div className="text-red-400 text-sm">
          概览数据加载失败，请稍后重试。
        </div>
      )}

      {overviewQuery.data && (
        <div className="grid gap-4 md:grid-cols-3">
          <KpiCard
            title="日活跃用户"
            value={overviewQuery.data.ga4.dau.current}
            yesterday={overviewQuery.data.ga4.dau.yesterday}
          />
          <KpiCard
            title="会话数"
            value={overviewQuery.data.ga4.sessions.current}
            yesterday={overviewQuery.data.ga4.sessions.yesterday}
          />
          <KpiCard
            title="页面浏览量"
            value={overviewQuery.data.ga4.page_views.current}
            yesterday={overviewQuery.data.ga4.page_views.yesterday}
          />
          <KpiCard
            title="GSC 展示"
            value={overviewQuery.data.gsc.impressions.current}
            yesterday={overviewQuery.data.gsc.impressions.yesterday}
          />
          <KpiCard
            title="GSC 点击"
            value={overviewQuery.data.gsc.clicks.current}
            yesterday={overviewQuery.data.gsc.clicks.yesterday}
          />
          <KpiCard
            title="GSC 平均排名"
            value={overviewQuery.data.gsc.avg_position.current}
            yesterday={overviewQuery.data.gsc.avg_position.yesterday}
            invert
          />
        </div>
      )}
    </div>
  );
}

interface KpiCardProps {
  title: string;
  value: number | null;
  yesterday: number | null;
  invert?: boolean;
}

function KpiCard({ title, value, yesterday, invert }: KpiCardProps) {
  const delta =
    value != null && yesterday != null && yesterday !== 0
      ? ((value - yesterday) / Math.abs(yesterday)) * 100
      : null;

  const trendPositive = delta != null ? (invert ? delta < 0 : delta > 0) : null;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-xs text-slate-400 mb-1">{title}</div>
      <div className="text-xl font-semibold">
        {value != null ? Math.round(value).toLocaleString("zh-CN") : "-"}
      </div>
      {delta != null && (
        <div
          className={
            "mt-1 text-xs " +
            (trendPositive === null
              ? "text-slate-400"
              : trendPositive
              ? "text-emerald-400"
              : "text-red-400")
          }
        >
          较昨日{" "}
          {delta > 0 ? "+" : ""}
          {delta.toFixed(1)}%
        </div>
      )}
    </div>
  );
}

