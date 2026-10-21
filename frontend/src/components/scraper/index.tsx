"use client";

import { useRef } from "react";
import { useScraper } from "@/hooks/use-scraper";
import { ScraperForm } from "./scraper-form";
import { ScraperResult } from "./scraper-result";
import { StatusBar } from "./status-bar";
import { toast } from "sonner";
import type { ScrapeRequest, ExampleScrape } from "@/types";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n-context";

const PROGRESS_TOAST_ID = "scrape-progress";

export function Scraper() {
  const { t, tOr } = useI18n();
  const resultRef = useRef<HTMLDivElement>(null);
  const {
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
  } = useScraper();

  const handleSubmit = async (request: ScrapeRequest) => {
    // One toast per run, under a fixed id: the "starting" toast is replaced by
    // the outcome instead of stacking under it. It used to stay on screen next
    // to a second toast repeating the error already shown in the result panel.
    toast.loading(t("toast.starting"), { id: PROGRESS_TOAST_ID });

    const response = await scrape(request);

    if (response?.success) {
      const suffix = response.is_sample
        ? t("toast.sample")
        : response.cache_hit
          ? t("toast.fromCache")
          : "";
      toast.success(`${t("toast.success")}${suffix}`, { id: PROGRESS_TOAST_ID });
    } else {
      // The failure is explained once, in the result panel.
      toast.dismiss(PROGRESS_TOAST_ID);
    }

    // On a phone the panel sits below the form; bring the outcome into view.
    resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
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
      {/* Falha ao abrir sessao dita no topo, antes de o visitante gastar tempo
          preenchendo um formulario que ja sabemos que vai falhar. */}
      {sessionError && (
        <div className="rounded-md border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-800">
          {t(sessionError)}
        </div>
      )}

      {/* Example buttons */}
      {examples.length > 0 && (
        <div className="space-y-2 sm:space-y-0 sm:flex sm:flex-wrap sm:items-center sm:gap-2">
          <span className="block text-sm text-muted-foreground sm:inline">
            {t("samples.label")}
          </span>
          <div className="grid grid-cols-2 gap-2 sm:contents">
            {examples.map((example) => (
              <button
                key={example.id}
                type="button"
                onClick={() => handleExampleClick(example)}
                disabled={isLoading}
                className="inline-flex items-center justify-center gap-1.5 px-3 py-2 text-sm rounded-md border border-border/50 bg-muted/30 hover:bg-muted/60 transition-colors disabled:opacity-50 disabled:cursor-not-allowed sm:py-1.5"
              >
                {tOr(`example.${example.id}`, example.name)}
                <Badge variant="secondary" className="text-[10px] px-1">
                  {t("samples.badge")}
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
        <div ref={resultRef} className="scroll-mt-20">
          <ScraperResult
            result={result}
            error={error}
            onClear={clearResult}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <StatusBar health={health} session={session} />
      </div>
    </div>
  );
}
