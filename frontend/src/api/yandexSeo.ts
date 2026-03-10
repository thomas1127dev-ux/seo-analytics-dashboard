import { apiClient } from "./client";
import type { SearchOverviewMetrics } from "./overview";
import type { SeoListResponse } from "./googleSeo";

export async function fetchYandexSeoSummary(params: {
  projectId: number;
  startDate: string;
  endDate: string;
}) {
  const { projectId, startDate, endDate } = params;
  const res = await apiClient.get<SearchOverviewMetrics>(
    "/api/dashboard/yandex-seo/summary",
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

export async function fetchYandexSeoQueries(params: {
  projectId: number;
  startDate: string;
  endDate: string;
  limit?: number;
}) {
  const { projectId, startDate, endDate, limit = 100 } = params;
  const res = await apiClient.get<SeoListResponse>(
    "/api/dashboard/yandex-seo/queries",
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

