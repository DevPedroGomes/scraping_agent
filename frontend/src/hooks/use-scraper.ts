"use client";

import { useState, useCallback, useEffect } from "react";
import { apiClient } from "@/lib/api";
import type {
  ScrapeRequest,
  ScrapeResponse,
  SessionInfo,
  HealthResponse,
  Model
} from "@/types";

// Fallback models in case API is unreachable
const FALLBACK_MODELS: Model[] = [
  // DeepSeek (Budget - Best Value)
  {
    id: "deepseek-v3",
    name: "DeepSeek V3",
    provider: "deepseek",
    description: "Best value - 95% GPT-4 quality at 5% cost",
    tier: "budget",
    input_price: 0.27,
    output_price: 1.10
  },
  {
    id: "deepseek-chat",
    name: "DeepSeek Chat",
    provider: "deepseek",
    description: "Cheapest option - Great for simple extractions",
    tier: "budget",
    input_price: 0.14,
    output_price: 0.28
  },
  // Gemini
  {
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    provider: "gemini",
    description: "Fast with 1M context window",
    tier: "standard",
    input_price: 0.30,
    output_price: 2.50
  },
  // OpenAI
  {
    id: "gpt-5-mini",
    name: "GPT-5 Mini",
    provider: "openai",
    description: "Balanced speed and intelligence",
    tier: "standard",
    input_price: 0.25,
    output_price: 2.00
  },
  // Anthropic
  {
    id: "claude-haiku-4.5",
    name: "Claude Haiku 4.5",
    provider: "anthropic",
    description: "Fastest Claude - Great for structured output",
    tier: "standard",
    input_price: 1.00,
    output_price: 5.00
  },
  // Grok
  {
    id: "grok-4-fast",
    name: "Grok 4 Fast",
    provider: "grok",
    description: "Fast with 2M context window",
    tier: "budget",
    input_price: 0.20,
    output_price: 0.50
  },
];

export function useScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScrapeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [models, setModels] = useState<Model[]>(FALLBACK_MODELS);

  const initSession = useCallback(async () => {
    try {
      const existingSessionId = apiClient.getSessionId();

      if (existingSessionId) {
        try {
          const sessionInfo = await apiClient.getSession(existingSessionId);
          setSession(sessionInfo);
          return;
        } catch {
          apiClient.clearSession();
        }
      }

      const newSession = await apiClient.createSession();
      setSession(newSession);
    } catch (err) {
      console.error("Failed to initialize session:", err);
    }
  }, []);

  const fetchHealth = useCallback(async () => {
    try {
      const healthInfo = await apiClient.getHealth();
      setHealth(healthInfo);
    } catch (err) {
      console.error("Failed to fetch health:", err);
    }
  }, []);

  const fetchModels = useCallback(async () => {
    try {
      const response = await apiClient.getModels();
      setModels(response.models);
    } catch (err) {
      console.error("Failed to fetch models, using fallback:", err);
      setModels(FALLBACK_MODELS);
    }
  }, []);

  const scrape = useCallback(async (request: ScrapeRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.scrape(request);
      setResult(response);

      if (!response.success && response.error) {
        setError(response.error);
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  useEffect(() => {
    initSession();
    fetchHealth();
    fetchModels();
  }, [initSession, fetchHealth, fetchModels]);

  return {
    isLoading,
    result,
    error,
    session,
    health,
    models,
    scrape,
    clearResult,
    refreshHealth: fetchHealth,
  };
}
