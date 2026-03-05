// AI Provider types
export type ModelProvider = "groq" | "openai" | "deepseek" | "gemini" | "anthropic" | "grok";

// Model types across all providers
export type ModelType =
  // Groq (FREE - Open Source Models)
  | "llama-3.3-70b-versatile"
  | "llama-3.1-8b-instant"
  | "mixtral-8x7b-32768"
  | "gemma2-9b-it"
  // DeepSeek (Budget)
  | "deepseek-chat"
  | "deepseek-v3"
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
  | "claude-haiku-4.5"
  | "claude-sonnet-4.5"
  | "claude-opus-4.5"
  // xAI Grok
  | "grok-4-fast"
  | "grok-4";

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
  // Markdown info
  markdown_used: boolean;
  token_reduction?: number;
  // Validation info
  validation_passed?: boolean;
  validation_errors?: string[];
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
  "llama-3.3-70b-versatile": "groq",
  "llama-3.1-8b-instant": "groq",
  "mixtral-8x7b-32768": "groq",
  "gemma2-9b-it": "groq",
  // DeepSeek
  "deepseek-chat": "deepseek",
  "deepseek-v3": "deepseek",
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
  "claude-haiku-4.5": "anthropic",
  "claude-sonnet-4.5": "anthropic",
  "claude-opus-4.5": "anthropic",
  // Grok
  "grok-4-fast": "grok",
  "grok-4": "grok",
};

// Provider display names
export const PROVIDER_NAMES: Record<ModelProvider, string> = {
  groq: "Groq (FREE)",
  openai: "OpenAI",
  deepseek: "DeepSeek",
  gemini: "Google Gemini",
  anthropic: "Anthropic",
  grok: "xAI Grok",
};

// Provider API key labels
export const PROVIDER_API_KEY_LABELS: Record<ModelProvider, string> = {
  groq: "Groq API Key (FREE)",
  openai: "OpenAI API Key",
  deepseek: "DeepSeek API Key",
  gemini: "Google AI API Key",
  anthropic: "Anthropic API Key",
  grok: "xAI API Key",
};
