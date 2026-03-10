import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import {
  fetchGoogleSeoSummary,
  fetchGoogleSeoQueries,
  fetchGoogleSeoPages
} from "../api/googleSeo";
import type { SearchOverviewMetrics } from "../api/overview";
import { FiltersRow } from "../components/FiltersRow";
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

export function GoogleSEOPage() {
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
    queryKey: ["google-seo-summary", projectId, startDate, endDate],
    queryFn: () =>
      fetchGoogleSeoSummary({
        projectId: projectId as number,
        startDate,
        endDate
      }),
    enabled: projectId != null
  });

  const queriesQuery = useQuery({
    queryKey: ["google-seo-queries", projectId, startDate, endDate],
    queryFn: () =>
      fetchGoogleSeoQueries({
        projectId: projectId as number,
        startDate,
        endDate,
        limit: 100
      }),
    enabled: projectId != null
  });

  const pagesQuery = useQuery({
    queryKey: ["google-seo-pages", projectId, startDate, endDate],
    queryFn: () =>
      fetchGoogleSeoPages({
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
      <FiltersRow
        projects={projects}
        projectId={projectId}
        onProjectChange={setProjectId}
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
        defaultDays={DEFAULT_DAYS}
      />

      {summaryQuery.data && (
        <div className="grid gap-4 md:grid-cols-4">
          <SeoKpi
            title="展示"
            metric={summaryQuery.data.impressions}
            expectedDate={endDate}
          />
          <SeoKpi
            title="点击"
            metric={summaryQuery.data.clicks}
            expectedDate={endDate}
          />
          <SeoKpi
            title="CTR"
            metric={summaryQuery.data.ctr}
            expectedDate={endDate}
            transform={(v) => v * 100}
            suffix="%"
          />
          <SeoKpi
            title="平均排名"
            metric={summaryQuery.data.avg_position}
            expectedDate={endDate}
            invert
          />
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <div className="glass-card p-4">
          <div className="section-title">
            <span className="section-title-dot" />
            <span>关键词点击 TOP</span>
          </div>
          {queriesQuery.isLoading && <div>加载中...</div>}
          {queriesQuery.isError && (
            <div className="text-red-400 text-sm">关键词数据加载失败。</div>
          )}
          {queriesQuery.data && (
            <div className="space-y-3 pt-1">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={queriesQuery.data.items.slice(0, 15).map((i) => ({
                      name:
                        i.key.length > 18 ? i.key.slice(0, 18) + "…" : i.key,
                      clicks: i.clicks
                    }))}
                    layout="vertical"
                    margin={{ left: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis
                      type="category"
                      dataKey="name"
                      stroke="#64748b"
                      width={90}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#020617",
                        borderColor: "#1e293b",
                        borderRadius: 8
                      }}
                    />
                    <Bar dataKey="clicks" fill="#38bdf8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <SeoTable items={queriesQuery.data.items} keyLabel="关键词" />
            </div>
          )}
        </div>
        <div className="glass-card p-4">
          <div className="section-title">
            <span className="section-title-dot" />
            <span>页面点击 TOP</span>
          </div>
          {pagesQuery.isLoading && <div>加载中...</div>}
          {pagesQuery.isError && (
            <div className="text-red-400 text-sm">页面数据加载失败。</div>
          )}
          {pagesQuery.data && (
            <div className="space-y-3 pt-1">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={pagesQuery.data.items.slice(0, 15).map((i) => ({
                      name:
                        i.key.length > 24 ? i.key.slice(0, 24) + "…" : i.key,
                      clicks: i.clicks
                    }))}
                    layout="vertical"
                    margin={{ left: 80 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis
                      type="category"
                      dataKey="name"
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
                    <Bar dataKey="clicks" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <SeoTable items={pagesQuery.data.items} keyLabel="页面" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface SeoKpiProps {
  title: string;
  metric: SearchOverviewMetrics["impressions"];
  expectedDate: string;
  transform?: (v: number) => number;
  invert?: boolean;
  suffix?: string;
}

function SeoKpi({
  title,
  metric,
  expectedDate,
  transform,
  invert,
  suffix = ""
}: SeoKpiProps) {
  const lastPoint = [...metric.trend_7d].reverse().find((p) => p.value != null);
  const secondLastPoint = [...metric.trend_7d]
    .reverse()
    .filter((p) => p.value != null)
    .slice(1, 2)[0];

  const rawCurrent = lastPoint?.value ?? null;
  const rawYesterday = secondLastPoint?.value ?? null;

  const current =
    rawCurrent != null && transform ? transform(rawCurrent) : rawCurrent;
  const yesterday =
    rawYesterday != null && transform ? transform(rawYesterday) : rawYesterday;

  const delta =
    current != null && yesterday != null && yesterday !== 0
      ? ((current - yesterday) / Math.abs(yesterday)) * 100
      : null;

  const trendPositive = delta != null ? (invert ? delta < 0 : delta > 0) : null;

  return (
    <div className="glass-card p-3">
      <div className="text-xs text-slate-400 mb-1 flex items-center justify-between">
        {title}
        {lastPoint && lastPoint.date !== expectedDate && (
          <span className="ml-1 text-[10px] text-slate-500">
            （数据日期 {lastPoint.date}）
          </span>
        )}
      </div>
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

interface SeoTableProps {
  items: {
    key: string;
    clicks: number;
    impressions: number;
    ctr: number;
    avg_position: number;
  }[];
  keyLabel: string;
}

function SeoTable({ items, keyLabel }: SeoTableProps) {
  return (
    <div className="border border-slate-800 rounded">
      <table className="w-full text-sm border-collapse">
        <thead className="text-slate-400">
          <tr>
            <th className="border-b border-slate-800 py-1 text-left">
              {keyLabel}
            </th>
            <th className="border-b border-slate-800 py-1 text-right">点击</th>
            <th className="border-b border-slate-800 py-1 text-right">展示</th>
            <th className="border-b border-slate-800 py-1 text-right">CTR</th>
            <th className="border-b border-slate-800 py-1 text-right">
              平均排名
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
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
              <td className="py-1 text-right">
                {i.avg_position.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

