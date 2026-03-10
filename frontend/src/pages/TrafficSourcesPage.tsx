import { useMemo, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchTrafficSources } from "../api/traffic";
import { SmartSelect } from "../components/SmartSelect";
import { DateButton } from "../components/DateButton";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

const DEFAULT_DAYS = 7;

function formatDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export function TrafficSourcesPage() {
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

      {trafficQuery.isLoading && (
        <div className="glass-card flex items-center justify-center py-10 text-sm text-slate-300">
          正在加载流量来源数据…
        </div>
      )}
      {trafficQuery.isError && (
        <div className="text-red-400 text-sm">流量来源数据加载失败。</div>
      )}

      {trafficQuery.data && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="glass-card p-4">
            <div className="section-title">
              <span className="section-title-dot" />
              <span>来源占比</span>
            </div>
            <div className="h-64 pt-1">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={trafficQuery.data.sources}
                    dataKey="sessions"
                    nameKey="channel"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {trafficQuery.data.sources.map((_, idx) => (
                      <Cell
                        key={idx}
                        fill={["#22c55e", "#38bdf8", "#f97316", "#a855f7", "#e11d48"][
                          idx % 5
                        ]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#020617",
                      borderColor: "#1e293b",
                      borderRadius: 8
                    }}
                    labelStyle={{ color: "#e5e7eb" }}
                    itemStyle={{ color: "#e5e7eb" }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="glass-card p-4">
            <div className="section-title">
              <span className="section-title-dot" />
              <span>会话趋势（按渠道）</span>
            </div>
            <div className="h-64 pt-1">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={aggregateTrend(trafficQuery.data.trend_7d)}
                  margin={{ left: -20 }}
                >
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
                  {Object.keys(
                    aggregateTrend(trafficQuery.data.trend_7d)[0] ?? {}
                  )
                    .filter((k) => k !== "date")
                    .map((ch, idx) => (
                      <Line
                        key={ch}
                        type="monotone"
                        dataKey={ch}
                        name={ch}
                        stroke={
                          ["#22c55e", "#38bdf8", "#f97316", "#a855f7", "#e11d48"][
                            idx % 5
                          ]
                        }
                        strokeWidth={2}
                        dot={false}
                      />
                    ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function aggregateTrend(
  points: { date: string; channel: string; sessions: number }[]
) {
  const map: Record<string, Record<string, number>> = {};
  for (const p of points) {
    if (!map[p.date]) map[p.date] = { date: p.date } as any;
    map[p.date][p.channel] = (map[p.date][p.channel] || 0) + p.sessions;
  }
  return Object.values(map);
}

