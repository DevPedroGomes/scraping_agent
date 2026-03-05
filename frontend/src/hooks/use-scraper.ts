"use client";

import { useState, useCallback, useEffect } from "react";
import { apiClient } from "@/lib/api";
import type {
  ScrapeRequest,
  ScrapeResponse,
  SessionInfo,
  HealthResponse,
  Model,
  ExampleScrape,
} from "@/types";

// Fallback models in case API is unreachable
const FALLBACK_MODELS: Model[] = [
  {
    id: "llama-3.3-70b-versatile",
    name: "Llama 3.3 70B",
    provider: "groq",
    description: "FREE - Best open source model, rivals GPT-4",
    tier: "free",
    input_price: 0.00,
    output_price: 0.00
  },
  {
    id: "mixtral-8x7b-32768",
    name: "Mixtral 8x7B",
    provider: "groq",
    description: "FREE - High quality MoE model with 32K context",
    tier: "free",
    input_price: 0.00,
    output_price: 0.00
  },
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
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    provider: "gemini",
    description: "Fast with 1M context window",
    tier: "standard",
    input_price: 0.30,
    output_price: 2.50
  },
  {
    id: "gpt-5-mini",
    name: "GPT-5 Mini",
    provider: "openai",
    description: "Balanced speed and intelligence",
    tier: "standard",
    input_price: 0.25,
    output_price: 2.00
  },
  {
    id: "claude-haiku-4.5",
    name: "Claude Haiku 4.5",
    provider: "anthropic",
    description: "Fastest Claude - Great for structured output",
    tier: "standard",
    input_price: 1.00,
    output_price: 5.00
  },
];

export function useScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScrapeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [models, setModels] = useState<Model[]>(FALLBACK_MODELS);
  const [examples, setExamples] = useState<ExampleScrape[]>([]);

  const refreshSession = useCallback(async () => {
    const sessionId = apiClient.getSessionId();
    if (sessionId) {
      try {
        const sessionInfo = await apiClient.getSession(sessionId);
        setSession(sessionInfo);
      } catch {
        // Session may have expired
      }
    }
  }, []);

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

  const fetchExamples = useCallback(async () => {
    try {
      const response = await apiClient.getExamples();
      setExamples(response.examples);
    } catch (err) {
      console.error("Failed to fetch examples:", err);
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

      // Refresh session to get updated scrape counter
      await refreshSession();

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [refreshSession]);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  useEffect(() => {
    initSession();
    fetchHealth();
    fetchModels();
    fetchExamples();
  }, [initSession, fetchHealth, fetchModels, fetchExamples]);

  return {
    isLoading,
    result,
    error,
    session,
    health,
    models,
    examples,
    scrape,
    clearResult,
    refreshHealth: fetchHealth,
  };
}
