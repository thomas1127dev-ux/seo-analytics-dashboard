import { apiClient } from "./client";
import type { SearchOverviewMetrics } from "./overview";

export interface SeoItem {
  key: string;
  clicks: number;
  impressions: number;
  ctr: number;
  avg_position: number;
}

export interface SeoListResponse {
  project_id: number;
  start_date: string;
  end_date: string;
  items: SeoItem[];
}

export async function fetchGoogleSeoSummary(params: {
  projectId: number;
  startDate: string;
  endDate: string;
}) {
  const { projectId, startDate, endDate } = params;
  const res = await apiClient.get<SearchOverviewMetrics>(
    "/api/dashboard/google-seo/summary",
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

export async function fetchGoogleSeoQueries(params: {
  projectId: number;
  startDate: string;
  endDate: string;
  limit?: number;
}) {
  const { projectId, startDate, endDate, limit = 100 } = params;
  const res = await apiClient.get<SeoListResponse>(
    "/api/dashboard/google-seo/queries",
    {
      params: {
        project_id: projectId,
        start_date: startDate,
        end_date: endDate,
        limit
      }
    }
  );
  return res.data;
}

export async function fetchGoogleSeoPages(params: {
  projectId: number;
  startDate: string;
  endDate: string;
  limit?: number;
}) {
  const { projectId, startDate, endDate, limit = 100 } = params;
  const res = await apiClient.get<SeoListResponse>(
    "/api/dashboard/google-seo/pages",
    {
      params: {
        project_id: projectId,
        start_date: startDate,
        end_date: endDate,
        limit
      }
    }
  );
  return res.data;
}

