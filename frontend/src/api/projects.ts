import { apiClient } from "./client";

export interface Project {
  id: number;
  project_key: string;
  name: string;
  domain: string;
}

export async function fetchProjects() {
  const res = await apiClient.get<Project[]>("/api/projects");
  return res.data;
}

