"use client";

import { useScraper } from "@/hooks/use-scraper";
import { ScraperForm } from "./scraper-form";
import { ScraperResult } from "./scraper-result";
import { StatusBar } from "./status-bar";
import { toast } from "sonner";
import type { ScrapeRequest, ExampleScrape } from "@/types";
import { Badge } from "@/components/ui/badge";

export function Scraper() {
  const {
    isLoading,
    result,
    error,
    session,
    health,
    models,
    examples,
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

  const handleExampleClick = (example: ExampleScrape) => {
    handleSubmit({
      url: example.url,
      prompt: example.prompt,
      model: example.model,
      use_cache: true,
      stealth_mode: true,
      use_markdown: true,
    });
  };

  return (
    <div className="space-y-6">
      {/* Example buttons */}
      {examples.length > 0 && (
        <div className="space-y-2 sm:space-y-0 sm:flex sm:flex-wrap sm:items-center sm:gap-2">
          <span className="block text-sm text-muted-foreground sm:inline">Try an example:</span>
          <div className="grid grid-cols-2 gap-2 sm:contents">
            {examples.map((example) => (
              <button
                key={example.id}
                type="button"
                onClick={() => handleExampleClick(example)}
                disabled={isLoading}
                className="inline-flex items-center justify-center gap-1.5 px-3 py-2 text-sm rounded-md border border-border/50 bg-muted/30 hover:bg-muted/60 transition-colors disabled:opacity-50 disabled:cursor-not-allowed sm:py-1.5"
              >
                {example.name}
                <Badge variant="secondary" className="text-[10px] px-1">
                  FREE
                </Badge>
              </button>
            ))}
          </div>
        </div>
      )}

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
