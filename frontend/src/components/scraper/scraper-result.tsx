"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { ScrapeResponse } from "@/types";
import { PROVIDER_NAMES, type ModelProvider } from "@/types";
import { useI18n } from "@/lib/i18n-context";
import { describeError, describeValidationError, type UiError } from "@/lib/errors";
import type { Translate } from "@/lib/i18n";

interface ScraperResultProps {
  result: ScrapeResponse | null;
  error: UiError | null;
  onClear: () => void;
}

/**
 * The seal says what actually happened to the JSON. `validation_passed` is null
 * whenever no schema was sent: nothing checked the output, so the panel says
 * "no schema validation" instead of letting the page's promise of validated
 * JSON stand in for a check that never ran.
 */
function ValidationSeal({ result, t }: { result: ScrapeResponse; t: Translate }) {
  if (result.validation_passed === true) {
    return (
      <Badge className="text-xs bg-emerald-600 text-white" data-validation="passed">
        {t("validation.passed")}
      </Badge>
    );
  }
  if (result.validation_passed === false) {
    return (
      <Badge variant="destructive" className="text-xs" data-validation="failed">
        {t("validation.failed")}
      </Badge>
    );
  }
  return (
    <Badge
      variant="outline"
      className="text-xs border-amber-300 bg-amber-50 text-amber-800"
      title={t("validation.noneHint")}
      data-validation="none"
    >
      {t("validation.none")}
    </Badge>
  );
}

export function ScraperResult({ result, error, onClear }: ScraperResultProps) {
  const { t } = useI18n();
  const [viewMode, setViewMode] = useState<"json" | "markdown">("json");

  if (!result && !error) {
    return (
      <Card className="border-border/50 h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl">{t("result.title")}</CardTitle>
          <CardDescription>
            {t("result.emptyDesc")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-48 text-muted-foreground text-sm">
            {t("result.emptyBody")}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !result) {
    return (
      <Card className="border-border/50 h-full">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">{t("result.title")}</CardTitle>
              <CardDescription>{t("result.errorDesc")}</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={onClear}>
              {t("result.clear")}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>{describeError(error, t)}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  const providerName = result.provider_used
    ? PROVIDER_NAMES[result.provider_used as ModelProvider] || result.provider_used
    : null;

  const hasMarkdown = !!result.markdown_content;

  return (
    <Card className="border-border/50 h-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl flex items-center gap-2">
              {t("result.title")}
              <Badge variant={result.success ? "default" : "destructive"}>
                {result.success ? t("result.success") : t("result.error")}
              </Badge>
            </CardTitle>
            <CardDescription>
              {result.is_sample
                ? t("result.sampleDesc")
                : t("result.executed", { seconds: result.execution_time.toFixed(2) })}
              {!result.is_sample && result.model_used && t("result.using", { model: result.model_used })}
              {!result.is_sample && providerName && ` (${providerName})`}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={onClear}>
            {t("result.clear")}
          </Button>
        </div>

        {/* Metadata badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          {result.success && <ValidationSeal result={result} t={t} />}
          {result.is_sample ? (
            <Badge variant="outline" className="text-xs">
              {t("badge.sample")}
            </Badge>
          ) : result.cache_hit ? (
            <Badge variant="secondary" className="text-xs">
              {t("badge.cache")}
            </Badge>
          ) : null}
          {result.markdown_used && (
            <Badge variant="secondary" className="text-xs">
              Markdown
              {result.token_reduction ? ` (-${result.token_reduction.toFixed(0)}%)` : ""}
            </Badge>
          )}
          {result.content_truncated && (
            <Badge variant="destructive" className="text-xs">
              {t("badge.truncated")}
            </Badge>
          )}
          {result.tokens_used != null && result.tokens_used > 0 && (
            <Badge variant="outline" className="text-xs">
              {t("badge.tokens", { n: result.tokens_used.toLocaleString() })}
            </Badge>
          )}
          {result.estimated_cost !== undefined && result.estimated_cost !== null && result.estimated_cost > 0 && (
            <Badge variant="outline" className="text-xs">
              ~${result.estimated_cost.toFixed(4)}
            </Badge>
          )}
          {result.actions_executed > 0 && (
            <Badge variant="secondary" className="text-xs">
              {result.actions_executed === 1
                ? t("badge.actions.one")
                : t("badge.actions.other", { n: result.actions_executed })}
            </Badge>
          )}
          {/* Timing breakdown */}
          {result.fetch_time != null && (
            <Badge variant="outline" className="text-xs">
              {t("badge.fetch", { s: result.fetch_time.toFixed(2) })}
            </Badge>
          )}
          {result.parse_time != null && (
            <Badge variant="outline" className="text-xs">
              {t("badge.parse", { s: result.parse_time.toFixed(2) })}
            </Badge>
          )}
          {result.llm_time != null && (
            <Badge variant="outline" className="text-xs">
              {t("badge.llm", { s: result.llm_time.toFixed(2) })}
            </Badge>
          )}
          {result.scrapes_remaining != null && (
            <Badge
              variant={result.scrapes_remaining <= 1 ? "destructive" : "outline"}
              className="text-xs"
            >
              {result.scrapes_remaining === 1
                ? t("badge.left.one")
                : t("badge.left.other", { n: result.scrapes_remaining })}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Validation errors */}
        {result.validation_errors && result.validation_errors.length > 0 && (
          <Alert variant="destructive">
            <AlertDescription>
              <div className="font-semibold mb-1">{t("result.validationErrors")}</div>
              <ul className="list-disc list-inside text-sm">
                {result.validation_errors.map((err, i) => (
                  <li key={i}>{describeValidationError(err, t)}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {/* View mode toggle */}
        {result.success && hasMarkdown && (
          <div className="flex gap-1">
            <button
              type="button"
              onClick={() => setViewMode("json")}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                viewMode === "json"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted/50 text-muted-foreground hover:bg-muted"
              }`}
            >
              {t("result.viewJson")}
            </button>
            <button
              type="button"
              onClick={() => setViewMode("markdown")}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                viewMode === "markdown"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted/50 text-muted-foreground hover:bg-muted"
              }`}
            >
              {t("result.viewMarkdown")}
            </button>
          </div>
        )}

        {/* Main result */}
        {!result.success ? (
          <Alert variant="destructive">
            <AlertDescription>
              {describeError(
                { code: result.error_code ?? "unknown", message: result.error ?? "" },
                t
              )}
            </AlertDescription>
          </Alert>
        ) : viewMode === "markdown" && result.markdown_content ? (
          <div className="bg-muted/50 rounded-lg p-4 overflow-auto max-h-[500px]">
            <pre className="text-sm font-mono whitespace-pre-wrap break-words">
              {result.markdown_content}
            </pre>
          </div>
        ) : (
          <div className="bg-muted/50 rounded-lg p-4 overflow-auto max-h-[500px]">
            <pre className="text-sm font-mono whitespace-pre-wrap break-words">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
