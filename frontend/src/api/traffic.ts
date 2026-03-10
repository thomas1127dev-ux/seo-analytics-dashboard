import { apiClient } from "./client";

export interface TrafficSourceShare {
  channel: string;
  sessions: number;
  users: number;
  page_views: number;
  ratio: number;
}

export interface TrafficTrendPoint {
  date: string;
  channel: string;
  sessions: number;
}

export interface TrafficSourcesResponse {
  project_id: number;
  start_date: string;
  end_date: string;
  sources: TrafficSourceShare[];
  trend_7d: TrafficTrendPoint[];
}

export async function fetchTrafficSources(params: {
  projectId: number;
  startDate: string;
  endDate: string;
}) {
  const { projectId, startDate, endDate } = params;
  const res = await apiClient.get<TrafficSourcesResponse>(
    "/api/dashboard/traffic-sources",
    {
      params: {
        project_id: projectId,
        start_date: startDate,
        end_date: endDate
      }
    }
  );
  return res.data;
}

