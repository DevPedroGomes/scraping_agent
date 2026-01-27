export type ModelType =
  | "gpt-3.5-turbo"
  | "gpt-4"
  | "gpt-4-turbo"
  | "gpt-4o"
  | "gpt-4o-mini";

export type ActionType = "click" | "scroll" | "wait" | "type";

export interface Model {
  id: ModelType;
  name: string;
  description: string;
}

export interface PageAction {
  action: ActionType;
  selector?: string;
  value?: string;
  wait_ms?: number;
}

export interface OutputField {
  name: string;
  type: "string" | "number" | "boolean" | "array" | "object";
  description?: string;
  required?: boolean;
}

export interface ScrapeRequest {
  url: string;
  prompt: string;
  model: ModelType;
  api_key?: string;
  output_schema?: OutputField[];
  actions?: PageAction[];
  use_cache?: boolean;
  cache_ttl_minutes?: number;
}

export interface ScrapeResponse {
  success: boolean;
  data: unknown;
  error?: string;
  execution_time: number;
  timestamp: string;
  cache_hit: boolean;
  validation_passed?: boolean;
  validation_errors?: string[];
  actions_executed: number;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  requests_count: number;
}

export interface HealthResponse {
  status: string;
  active_sessions: number;
  max_sessions: number;
  version: string;
}

export interface ModelsResponse {
  models: Model[];
}
