"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { ScrapeResponse } from "@/types";
import { PROVIDER_NAMES, type ModelProvider } from "@/types";

interface ScraperResultProps {
  result: ScrapeResponse | null;
  error: string | null;
  onClear: () => void;
}

export function ScraperResult({ result, error, onClear }: ScraperResultProps) {
  const [viewMode, setViewMode] = useState<"json" | "markdown">("json");

  if (!result && !error) {
    return (
      <Card className="border-border/50 h-full">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl">Result</CardTitle>
          <CardDescription>
            Extracted data will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-48 text-muted-foreground text-sm">
            No results yet. Make a request to start.
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
              <CardTitle className="text-xl">Result</CardTitle>
              <CardDescription>An error occurred</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={onClear}>
              Clear
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
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
              Result
              <Badge variant={result.success ? "default" : "destructive"}>
                {result.success ? "Success" : "Error"}
              </Badge>
            </CardTitle>
            <CardDescription>
              Executed in {result.execution_time.toFixed(2)}s
              {result.model_used && ` using ${result.model_used}`}
              {providerName && ` (${providerName})`}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={onClear}>
            Clear
          </Button>
        </div>

        {/* Metadata badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          {result.cache_hit && (
            <Badge variant="secondary" className="text-xs">
              Cache Hit
            </Badge>
          )}
          {result.markdown_used && (
            <Badge variant="secondary" className="text-xs">
              Markdown
              {result.token_reduction && ` (-${result.token_reduction.toFixed(0)}%)`}
            </Badge>
          )}
          {result.content_truncated && (
            <Badge variant="destructive" className="text-xs">
              Content Truncated
            </Badge>
          )}
          {result.tokens_used && result.tokens_used > 0 && (
            <Badge variant="outline" className="text-xs">
              {result.tokens_used.toLocaleString()} tokens
            </Badge>
          )}
          {result.estimated_cost !== undefined && result.estimated_cost !== null && result.estimated_cost > 0 && (
            <Badge variant="outline" className="text-xs">
              ~${result.estimated_cost.toFixed(4)}
            </Badge>
          )}
          {result.actions_executed > 0 && (
            <Badge variant="secondary" className="text-xs">
              {result.actions_executed} action{result.actions_executed > 1 ? "s" : ""} executed
            </Badge>
          )}
          {result.validation_passed !== null && result.validation_passed !== undefined && (
            <Badge
              variant={result.validation_passed ? "default" : "destructive"}
              className="text-xs"
            >
              {result.validation_passed ? "Schema Valid" : "Schema Invalid"}
            </Badge>
          )}
          {/* Timing breakdown */}
          {result.fetch_time != null && (
            <Badge variant="outline" className="text-xs">
              Fetch: {result.fetch_time.toFixed(2)}s
            </Badge>
          )}
          {result.parse_time != null && (
            <Badge variant="outline" className="text-xs">
              Parse: {result.parse_time.toFixed(2)}s
            </Badge>
          )}
          {result.llm_time != null && (
            <Badge variant="outline" className="text-xs">
              LLM: {result.llm_time.toFixed(2)}s
            </Badge>
          )}
          {result.scrapes_remaining != null && (
            <Badge
              variant={result.scrapes_remaining <= 1 ? "destructive" : "outline"}
              className="text-xs"
            >
              {result.scrapes_remaining} scrape{result.scrapes_remaining !== 1 ? "s" : ""} left
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Validation errors */}
        {result.validation_errors && result.validation_errors.length > 0 && (
          <Alert variant="destructive">
            <AlertDescription>
              <div className="font-semibold mb-1">Validation Errors:</div>
              <ul className="list-disc list-inside text-sm">
                {result.validation_errors.map((err, i) => (
                  <li key={i}>{err}</li>
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
              JSON Result
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
              Processed Content
            </button>
          </div>
        )}

        {/* Main result */}
        {result.error ? (
          <Alert variant="destructive">
            <AlertDescription>{result.error}</AlertDescription>
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
