import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchOverview, type MetricWithTrend } from "../api/overview";
import { FiltersRow } from "../components/FiltersRow";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function OverviewPage() {
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

      {overviewQuery.isLoading && (
        <div className="glass-card flex items-center justify-center py-10 text-sm text-slate-300">
          正在拉取概览数据…
        </div>
      )}
      {overviewQuery.isError && (
        <div className="text-red-400 text-sm">
          概览数据加载失败，请稍后重试。
        </div>
      )}

      {overviewQuery.data && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            {/* GA4 核心指标 */}
            <KpiCard
              title="日活跃用户"
              metric={overviewQuery.data.ga4.dau}
              expectedDate={endDate}
            />
            <KpiCard
              title="新用户数"
              metric={overviewQuery.data.ga4.new_users}
              expectedDate={endDate}
            />
            <KpiCard
              title="老用户数"
              metric={overviewQuery.data.ga4.returning_users}
              expectedDate={endDate}
            />

            <KpiCard
              title="次日留存人数"
              metric={overviewQuery.data.ga4.retention_d1}
              expectedDate={endDate}
            />
            <KpiCard
              title="3 日留存人数"
              metric={overviewQuery.data.ga4.retention_d3}
              expectedDate={endDate}
            />
            <KpiCard
              title="7 日留存人数"
              metric={overviewQuery.data.ga4.retention_d7}
              expectedDate={endDate}
            />

            {/* GSC 指标 */}
            <KpiCard
              title="GSC 展示"
              metric={overviewQuery.data.gsc.impressions}
              expectedDate={endDate}
            />
            <KpiCard
              title="GSC 点击"
              metric={overviewQuery.data.gsc.clicks}
              expectedDate={endDate}
            />
            <KpiCard
              title="GSC 平均排名"
              metric={overviewQuery.data.gsc.avg_position}
              expectedDate={endDate}
              invert
            />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <TrendCard
              title="会话趋势（GA4）"
              data={overviewQuery.data.ga4.sessions.trend_7d}
              color="#22c55e"
            />
            <TrendCard
              title="点击趋势（GSC）"
              data={overviewQuery.data.gsc.clicks.trend_7d}
              color="#38bdf8"
            />
          </div>

          <RetentionHeatmap
            endDate={endDate}
            d1={overviewQuery.data.ga4.retention_d1.trend_7d}
            d3={overviewQuery.data.ga4.retention_d3.trend_7d}
            d7={overviewQuery.data.ga4.retention_d7.trend_7d}
          />
        </>
      )}
    </div>
  );
}

interface KpiCardProps {
  title: string;
  metric: MetricWithTrend;
  expectedDate: string;
  invert?: boolean;
}

function KpiCard({ title, metric, expectedDate, invert }: KpiCardProps) {
  const lastPoint = [...metric.trend_7d].reverse().find((p) => p.value != null);
  const secondLastPoint = [...metric.trend_7d]
    .reverse()
    .filter((p) => p.value != null)
    .slice(1, 2)[0];

  const value = lastPoint?.value ?? null;
  const yesterday = secondLastPoint?.value ?? null;

  const delta =
    value != null && yesterday != null && yesterday !== 0
      ? ((value - yesterday) / Math.abs(yesterday)) * 100
      : null;

  const trendPositive = delta != null ? (invert ? delta < 0 : delta > 0) : null;

  return (
    <div className="glass-card p-4 transition-colors hover:border-emerald-500/60">
      <div className="text-xs text-slate-400 mb-1">
        {title}
        {lastPoint && lastPoint.date !== expectedDate && (
          <span className="ml-1 text-[10px] text-slate-500">
            （数据日期 {lastPoint.date}）
          </span>
        )}
      </div>
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

interface TrendCardProps {
  title: string;
  data: { date: string; value: number | null }[];
  color: string;
}

function TrendCard({ title, data, color }: TrendCardProps) {
  const chartData = data.map((d) => ({
    date: d.date.slice(5), // MM-DD
    value: d.value ?? 0
  }));

  return (
    <div className="glass-card p-4">
      <div className="section-title">
        <span className="section-title-dot" />
        <span>{title}</span>
      </div>
      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#020617",
                borderColor: "#1e293b",
                borderRadius: 8
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

interface RetentionHeatmapProps {
  endDate: string;
  d1: { date: string; value: number | null }[];
  d3: { date: string; value: number | null }[];
  d7: { date: string; value: number | null }[];
}

function RetentionHeatmap({ endDate, d1, d3, d7 }: RetentionHeatmapProps) {
  const rows = [
    { key: "d1", label: "次日留存人数", data: d1 },
    { key: "d3", label: "3 日留存人数", data: d3 },
    { key: "d7", label: "7 日留存人数", data: d7 }
  ];

  const allValues = rows.flatMap((row) =>
    row.data.map((p) => (p.value == null ? 0 : p.value))
  );
  const max = Math.max(0, ...allValues);

  const dates = d1.map((p) => p.date);

  const getCellColor = (value: number | null) => {
    if (value == null || max === 0) {
      return "rgba(15,23,42,0.9)"; // 很深的灰色，表示无数据
    }
    const ratio = Math.min(1, value / max);
    const lightness = 85 - ratio * 45; // 数值越大颜色越深
    return `hsl(199 89% ${lightness}%)`; // 接近 Tailwind sky- 系列
  };

  return (
    <div className="glass-card p-4">
      <div className="section-title mb-3">
        <span className="section-title-dot" />
        <span>留存热力图（人数越多颜色越深）</span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-center text-xs text-slate-200">
          <thead>
            <tr>
              <th className="py-1 px-2 text-left text-slate-400">留存窗口</th>
              {dates.map((d) => (
                <th key={d} className="py-1 px-2 text-slate-400">
                  {d.slice(5)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <td className="py-1 pr-2 text-left text-slate-300 whitespace-nowrap">
                  {row.label}
                </td>
                {row.data.map((p) => {
                  const value = p.value;
                  const bg = getCellColor(value);
                  return (
                    <td key={row.key + p.date} className="py-0.5 px-0.5">
                      <div
                        className="rounded-sm py-1"
                        style={{
                          backgroundColor: bg,
                          color: value != null ? "#0f172a" : "#64748b"
                        }}
                      >
                        {value != null ? Math.round(value).toLocaleString("zh-CN") : "-"}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-2 text-[10px] text-slate-500">
          区间结束日期：{endDate}；仅展示最近 {dates.length} 天的留存人数，颜色按每行最大值自动分级。
        </div>
      </div>
    </div>
  );
}

