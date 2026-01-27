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

export function useScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScrapeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [models, setModels] = useState<Model[]>([]);

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
      console.error("Failed to fetch models:", err);
      setModels([
        { id: "gpt-4o-mini", name: "GPT-4o Mini", description: "Fast and economical" },
        { id: "gpt-4o", name: "GPT-4o", description: "More accurate, multimodal" },
        { id: "gpt-4-turbo", name: "GPT-4 Turbo", description: "High performance" },
        { id: "gpt-4", name: "GPT-4", description: "Robust model" },
        { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo", description: "Economical" },
      ]);
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
      const errorMessage = err instanceof Error ? err.message : "Erro desconhecido";
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
