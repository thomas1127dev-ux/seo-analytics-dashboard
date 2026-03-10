import { apiClient } from "./client";

export interface ContentPageItem {
  page_path: string;
  page_views: number;
  avg_engagement_time: number;
  bounce_rate: number;
  growth_7d: number;
}

export interface ContentPerformanceResponse {
  project_id: number;
  start_date: string;
  end_date: string;
  pages: ContentPageItem[];
}

export async function fetchContentPerformance(params: {
  projectId: number;
  startDate: string;
  endDate: string;
  limit?: number;
}) {
  const { projectId, startDate, endDate, limit = 20 } = params;
  const res = await apiClient.get<ContentPerformanceResponse>(
    "/api/dashboard/content",
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

