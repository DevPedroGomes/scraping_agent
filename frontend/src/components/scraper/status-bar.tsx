"use client";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { HealthResponse, SessionInfo } from "@/types";

interface StatusBarProps {
  health: HealthResponse | null;
  session: SessionInfo | null;
}

export function StatusBar({ health, session }: StatusBarProps) {
  const scrapesExhausted = session
    ? session.scrape_count >= session.max_scrapes
    : false;

  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground">
      <div className="flex items-center gap-2">
        <span>Status:</span>
        <Badge variant={health?.status === "healthy" ? "default" : "destructive"} className="text-xs">
          {health?.status === "healthy" ? "Online" : "Offline"}
        </Badge>
      </div>

      <Separator orientation="vertical" className="h-4" />

      <div className="flex items-center gap-1">
        <span>Active sessions:</span>
        <span className="font-mono">
          {health?.active_sessions ?? "-"}/{health?.max_sessions ?? "-"}
        </span>
      </div>

      {session && (
        <>
          <Separator orientation="vertical" className="h-4" />
          <div className="flex items-center gap-1">
            <span>Scrapes:</span>
            <span
              className={`font-mono ${
                scrapesExhausted ? "text-red-400 font-semibold" : ""
              }`}
            >
              {session.scrape_count}/{session.max_scrapes}
            </span>
          </div>
        </>
      )}

      <Separator orientation="vertical" className="h-4" />

      <div className="flex items-center gap-1">
        <span>Version:</span>
        <span className="font-mono">{health?.version ?? "1.0.0"}</span>
      </div>
    </div>
  );
}
