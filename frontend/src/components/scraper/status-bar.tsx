"use client";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { HealthResponse, SessionInfo } from "@/types";
import { useI18n } from "@/lib/i18n-context";

interface StatusBarProps {
  health: HealthResponse | null;
  session: SessionInfo | null;
}

export function StatusBar({ health, session }: StatusBarProps) {
  const { t } = useI18n();
  const scrapesExhausted = session
    ? session.scrape_count >= session.max_scrapes
    : false;

  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground">
      <div className="flex items-center gap-2">
        <span>{t("status.status")}</span>
        <Badge variant={health?.status === "healthy" ? "default" : "destructive"} className="text-xs">
          {health?.status === "healthy" ? t("status.online") : t("status.offline")}
        </Badge>
      </div>

      {session && (
        <>
          <Separator orientation="vertical" className="h-4" />
          <div className="flex items-center gap-1">
            <span>{t("status.scrapes")}</span>
            <span
              className={`font-mono ${
                scrapesExhausted ? "text-red-600 font-semibold" : ""
              }`}
            >
              {session.scrape_count}/{session.max_scrapes}
            </span>
          </div>
        </>
      )}

      <Separator orientation="vertical" className="h-4" />

      <div className="flex items-center gap-1">
        <span>{t("status.version")}</span>
        <span className="font-mono">{health?.version ?? "1.0.0"}</span>
      </div>
    </div>
  );
}
