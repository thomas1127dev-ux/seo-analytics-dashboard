import { apiClient } from "./client";

export interface DailyPoint {
  date: string;
  value: number | null;
}

export interface MetricWithTrend {
  current: number | null;
  yesterday: number | null;
  trend_7d: DailyPoint[];
}

export interface Ga4OverviewMetrics {
  dau: MetricWithTrend;
  sessions: MetricWithTrend;
  page_views: MetricWithTrend;
  avg_engagement_time: MetricWithTrend;
  engagement_rate: MetricWithTrend;
  bounce_rate: MetricWithTrend;
}

export interface SearchOverviewMetrics {
  impressions: MetricWithTrend;
  clicks: MetricWithTrend;
  ctr: MetricWithTrend;
  avg_position: MetricWithTrend;
}

export interface OverviewResponse {
  project_id: number;
  start_date: string;
  end_date: string;
  ga4: Ga4OverviewMetrics;
  gsc: SearchOverviewMetrics;
  yandex: SearchOverviewMetrics;
}

export async function fetchOverview(params: {
  projectId: number;
  startDate: string;
  endDate: string;
}) {
  const { projectId, startDate, endDate } = params;
  const res = await apiClient.get<OverviewResponse>("/api/dashboard/overview", {
    params: {
      project_id: projectId,
      start_date: startDate,
      end_date: endDate
    }
  });
  return res.data;
}

