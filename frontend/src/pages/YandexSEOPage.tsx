import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import {
  fetchYandexSeoSummary,
  fetchYandexSeoQueries
} from "../api/yandexSeo";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function YandexSEOPage() {
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

  const summaryQuery = useQuery({
    queryKey: ["yandex-seo-summary", projectId, startDate, endDate],
    queryFn: () =>
      fetchYandexSeoSummary({
        projectId: projectId as number,
        startDate,
        endDate
      }),
    enabled: projectId != null
  });

  const queriesQuery = useQuery({
    queryKey: ["yandex-seo-queries", projectId, startDate, endDate],
    queryFn: () =>
      fetchYandexSeoQueries({
        projectId: projectId as number,
        startDate,
        endDate,
        limit: 100
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
        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
          <span>日期范围：</span>
          <input
            type="date"
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
            value={startDate}
            max={endDate}
            onChange={(e) => {
              if (!e.target.value) return;
              setStartDate(e.target.value);
            }}
          />
          <span>～</span>
          <input
            type="date"
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs"
            value={endDate}
            min={startDate}
            onChange={(e) => {
              if (!e.target.value) return;
              setEndDate(e.target.value);
            }}
          />
          <button
            className="ml-2 rounded border border-slate-700 px-2 py-1 text-xs hover:bg-slate-800"
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

      {summaryQuery.data && (
        <div className="grid gap-4 md:grid-cols-4">
          <SeoKpi
            title="展示"
            current={summaryQuery.data.impressions.current}
            yesterday={summaryQuery.data.impressions.yesterday}
          />
          <SeoKpi
            title="点击"
            current={summaryQuery.data.clicks.current}
            yesterday={summaryQuery.data.clicks.yesterday}
          />
          <SeoKpi
            title="CTR"
            current={
              summaryQuery.data.ctr.current != null
                ? summaryQuery.data.ctr.current * 100
                : null
            }
            yesterday={
              summaryQuery.data.ctr.yesterday != null
                ? summaryQuery.data.ctr.yesterday * 100
                : null
            }
            suffix="%"
          />
          <SeoKpi
            title="平均排名"
            current={summaryQuery.data.avg_position.current}
            yesterday={summaryQuery.data.avg_position.yesterday}
            invert
          />
        </div>
      )}

      <div>
        <h2 className="mb-2 text-sm font-semibold text-slate-200">
          查询词排行
        </h2>
        {queriesQuery.isLoading && <div>加载中...</div>}
        {queriesQuery.isError && (
          <div className="text-red-400 text-sm">查询词数据加载失败。</div>
        )}
        {queriesQuery.data && (
          <table className="w-full text-sm border-collapse border border-slate-800 rounded">
            <thead className="text-slate-400">
              <tr>
                <th className="border-b border-slate-800 py-1 text-left">
                  查询词
                </th>
                <th className="border-b border-slate-800 py-1 text-right">
                  点击
                </th>
                <th className="border-b border-slate-800 py-1 text-right">
                  展示
                </th>
                <th className="border-b border-slate-800 py-1 text-right">
                  CTR
                </th>
              </tr>
            </thead>
            <tbody>
              {queriesQuery.data.items.map((i) => (
                <tr key={i.key} className="border-b border-slate-900">
                  <td className="py-1 max-w-xs truncate" title={i.key}>
                    {i.key}
                  </td>
                  <td className="py-1 text-right">
                    {Math.round(i.clicks).toLocaleString("zh-CN")}
                  </td>
                  <td className="py-1 text-right">
                    {Math.round(i.impressions).toLocaleString("zh-CN")}
                  </td>
                  <td className="py-1 text-right">
                    {(i.ctr * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

interface SeoKpiProps {
  title: string;
  current: number | null;
  yesterday: number | null;
  invert?: boolean;
  suffix?: string;
}

function SeoKpi({
  title,
  current,
  yesterday,
  invert,
  suffix = ""
}: SeoKpiProps) {
  const delta =
    current != null && yesterday != null && yesterday !== 0
      ? ((current - yesterday) / Math.abs(yesterday)) * 100
      : null;

  const trendPositive = delta != null ? (invert ? delta < 0 : delta > 0) : null;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
      <div className="text-xs text-slate-400 mb-1">{title}</div>
      <div className="text-lg font-semibold">
        {current != null ? `${current.toFixed(1)}${suffix}` : "-"}
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
          较昨日 {delta > 0 ? "+" : ""}
          {delta.toFixed(1)}%
        </div>
      )}
    </div>
  );
}

