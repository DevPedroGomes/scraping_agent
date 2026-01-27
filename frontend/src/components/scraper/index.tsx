"use client";

import { useScraper } from "@/hooks/use-scraper";
import { ScraperForm } from "./scraper-form";
import { ScraperResult } from "./scraper-result";
import { StatusBar } from "./status-bar";
import { toast } from "sonner";
import type { ScrapeRequest } from "@/types";

export function Scraper() {
  const {
    isLoading,
    result,
    error,
    session,
    health,
    models,
    scrape,
    clearResult,
  } = useScraper();

  const handleSubmit = async (request: ScrapeRequest) => {
    toast.info("Starting data extraction...");

    const response = await scrape(request);

    if (response?.success) {
      const cacheMsg = response.cache_hit ? " (from cache)" : "";
      toast.success(`Data extracted successfully${cacheMsg}!`);
    } else if (response?.error || error) {
      toast.error(response?.error || error || "Error extracting data");
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <ScraperForm
          models={models}
          isLoading={isLoading}
          onSubmit={handleSubmit}
        />
        <ScraperResult
          result={result}
          error={error}
          onClear={clearResult}
        />
      </div>

      <div className="flex justify-center">
        <StatusBar health={health} session={session} />
      </div>
    </div>
  );
}
