import type {
  ScrapeRequest,
  ScrapeResponse,
  SessionInfo,
  HealthResponse,
  ModelsResponse
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private sessionId: string | null = null;

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (this.sessionId) {
      headers["X-Session-Id"] = this.sessionId;
    }

    if (options.headers) {
      const incomingHeaders = options.headers as Record<string, string>;
      Object.assign(headers, incomingHeaders);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  setSessionId(sessionId: string) {
    this.sessionId = sessionId;
    if (typeof window !== "undefined") {
      localStorage.setItem("scraper_session_id", sessionId);
    }
  }

  getSessionId(): string | null {
    if (typeof window !== "undefined" && !this.sessionId) {
      this.sessionId = localStorage.getItem("scraper_session_id");
    }
    return this.sessionId;
  }

  clearSession() {
    this.sessionId = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("scraper_session_id");
    }
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/api/v1/health");
  }

  async createSession(): Promise<SessionInfo> {
    const session = await this.request<SessionInfo>("/api/v1/session", {
      method: "POST",
    });
    this.setSessionId(session.session_id);
    return session;
  }

  async getSession(sessionId: string): Promise<SessionInfo> {
    return this.request<SessionInfo>(`/api/v1/session/${sessionId}`);
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.request(`/api/v1/session/${sessionId}`, {
      method: "DELETE",
    });
    this.clearSession();
  }

  async scrape(request: ScrapeRequest): Promise<ScrapeResponse> {
    return this.request<ScrapeResponse>("/api/v1/scrape", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getModels(): Promise<ModelsResponse> {
    return this.request<ModelsResponse>("/api/v1/models");
  }
}

export const apiClient = new ApiClient();
