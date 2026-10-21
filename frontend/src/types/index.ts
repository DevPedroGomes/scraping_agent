// AI Provider types
export type ModelProvider = "groq" | "openai" | "deepseek" | "gemini" | "anthropic" | "grok";

// Model types across all providers
export type ModelType =
  // Groq (FREE - Open Source Models)
  | "openai/gpt-oss-120b"
  | "openai/gpt-oss-20b"
  // DeepSeek (Budget)
  | "deepseek-chat"
  // Gemini
  | "gemini-2.5-flash-lite"
  | "gemini-2.5-flash"
  | "gemini-2.5-pro"
  // OpenAI GPT-5
  | "gpt-5-nano"
  | "gpt-5-mini"
  | "gpt-5"
  // OpenAI Legacy
  | "gpt-4o-mini"
  | "gpt-4o"
  // Anthropic Claude
  | "claude-haiku-4-5"
  | "claude-sonnet-4-6"
  | "claude-opus-4-6"
  // xAI Grok
  | "grok-4-fast-non-reasoning"
  | "grok-4-0709";

// Cost tier for smart routing
export type CostTier = "free" | "budget" | "standard" | "premium";

export type ActionType = "click" | "scroll" | "wait" | "type";

export interface Model {
  id: ModelType;
  name: string;
  provider: ModelProvider;
  description: string;
  tier: CostTier;
  input_price: number;
  output_price: number;
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
  cost_tier?: CostTier;
  output_schema?: OutputField[];
  actions?: PageAction[];
  use_cache?: boolean;
  cache_ttl_minutes?: number;
  stealth_mode?: boolean;
  use_markdown?: boolean;
}

export interface ScrapeResponse {
  success: boolean;
  data: unknown;
  error?: string;
  // Motivo da falha legivel por maquina; a interface traduz por ele.
  error_code?: string | null;
  execution_time: number;
  timestamp: string;
  // Model info
  model_used?: string;
  provider_used?: string;
  // Token usage
  tokens_used?: number;
  estimated_cost?: number;
  // Cache info
  cache_hit: boolean;
  // Amostra pre-gravada dos exemplos do showcase, nao um scrape ao vivo.
  is_sample?: boolean;
  // Markdown info
  markdown_used: boolean;
  token_reduction?: number;
  // Validation info. null/undefined = no schema was sent, so NOTHING was
  // validated; the UI must say so instead of implying the JSON was checked.
  validation_passed?: boolean | null;
  validation_errors?: string[] | null;
  // Actions info
  actions_executed: number;
  // Content truncation
  content_truncated?: boolean;
  // Intermediate content
  markdown_content?: string;
  // Timing breakdown
  fetch_time?: number;
  parse_time?: number;
  llm_time?: number;
  // Cost control
  scrapes_remaining?: number;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  requests_count: number;
  scrape_count: number;
  max_scrapes: number;
}

export interface HealthResponse {
  status: string;
  active_sessions: number;
  max_sessions: number;
  version: string;
  features: string[];
}

export interface ModelsResponse {
  models: Model[];
  default_model: string;
}

// Examples
export interface ExampleScrape {
  id: string;
  name: string;
  url: string;
  prompt: string;
  model: ModelType;
}

export interface ExamplesResponse {
  examples: ExampleScrape[];
}

// Helper to get provider from model
export const MODEL_TO_PROVIDER: Record<ModelType, ModelProvider> = {
  // Groq (FREE)
  "openai/gpt-oss-120b": "groq",
  "openai/gpt-oss-20b": "groq",
  // DeepSeek
  "deepseek-chat": "deepseek",
  // Gemini
  "gemini-2.5-flash-lite": "gemini",
  "gemini-2.5-flash": "gemini",
  "gemini-2.5-pro": "gemini",
  // OpenAI
  "gpt-5-nano": "openai",
  "gpt-5-mini": "openai",
  "gpt-5": "openai",
  "gpt-4o-mini": "openai",
  "gpt-4o": "openai",
  // Anthropic
  "claude-haiku-4-5": "anthropic",
  "claude-sonnet-4-6": "anthropic",
  "claude-opus-4-6": "anthropic",
  // Grok
  "grok-4-fast-non-reasoning": "grok",
  "grok-4-0709": "grok",
};

// Counted from the map above, never typed by hand: the page once showed
// "6 providers", "5 models" and a 16-model dropdown at the same time. A backend
// test (tests/test_modelos.py) keeps this map equal to the API catalog.
export const MODEL_COUNT = Object.keys(MODEL_TO_PROVIDER).length;
export const PROVIDER_COUNT = new Set(Object.values(MODEL_TO_PROVIDER)).size;

// Provider display names (the Groq label is translated in the UI)
export const PROVIDER_NAMES: Record<ModelProvider, string> = {
  groq: "Groq",
  openai: "OpenAI",
  deepseek: "DeepSeek",
  gemini: "Google Gemini",
  anthropic: "Anthropic",
  grok: "xAI Grok",
};

// Who issues the key, for the "<vendor> API key" label
export const PROVIDER_KEY_VENDORS: Record<ModelProvider, string> = {
  groq: "Groq",
  openai: "OpenAI",
  deepseek: "DeepSeek",
  gemini: "Google AI",
  anthropic: "Anthropic",
  grok: "xAI",
};
