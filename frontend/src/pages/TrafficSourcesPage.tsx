import { useMemo, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "../api/projects";
import { fetchTrafficSources } from "../api/traffic";
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
            <div className="h-64 rounded border border-slate-800 bg-slate-900/60 p-2">
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
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div>
            <h2 className="mb-2 text-sm font-semibold text-slate-200">
              会话趋势（按渠道）
            </h2>
            <div className="h-64 rounded border border-slate-800 bg-slate-900/60 p-2">
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

