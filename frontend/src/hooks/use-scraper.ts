"use client";

import { useState, useCallback, useEffect } from "react";
import { apiClient, ApiError } from "@/lib/api";
import type { UiError } from "@/lib/errors";
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
    id: "openai/gpt-oss-120b",
    name: "GPT-OSS 120B",
    provider: "groq",
    description: "Free - 120B open-weight model served by Groq",
    tier: "free",
    input_price: 0.00,
    output_price: 0.00
  },
  {
    id: "deepseek-chat",
    name: "DeepSeek V3.2",
    provider: "deepseek",
    description: "Best value - Cheap and capable (128K context)",
    tier: "budget",
    input_price: 0.28,
    output_price: 0.42
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
    input_price: 0.50,
    output_price: 5.00
  },
  {
    id: "claude-haiku-4-5",
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
  // Only failures WITHOUT a ScrapeResponse body land here (expired session,
  // network, client timeout). A failed scrape lives in `result`, so the panel
  // shows one message instead of the same error twice.
  const [error, setError] = useState<UiError | null>(null);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [models, setModels] = useState<Model[]>(FALLBACK_MODELS);
  const [examples, setExamples] = useState<ExampleScrape[]>([]);
  // Sem isto a falha ao abrir sessao so ia para o console: a tela ficava com
  // aparencia normal e o visitante so descobria ao clicar em Extract, recebendo
  // "Missing X-Session-Id header" — mensagem de API, nao de produto.
  // Holds an i18n key; the component translates it.
  const [sessionError, setSessionError] = useState<"session.tooMany" | "session.failed" | null>(null);

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
      setSessionError(null);
    } catch (err) {
      const detail = err instanceof Error ? err.message : "";
      setSessionError(detail.includes("this IP") ? "session.tooMany" : "session.failed");
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

      // Refresh session to get updated scrape counter
      await refreshSession();

      return response;
    } catch (err) {
      if (err instanceof ApiError) {
        setError({ code: err.code, message: err.message });
        if (err.code === "session_expired") {
          // The old id is useless now; open a fresh session so the next click
          // works instead of failing the same way again.
          apiClient.clearSession();
          await initSession();
        }
      } else {
        setError({ code: "unknown", message: err instanceof Error ? err.message : "" });
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [refreshSession, initSession]);

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
    sessionError,
    health,
    models,
    examples,
    scrape,
    clearResult,
    refreshHealth: fetchHealth,
  };
}
