"use client";

import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type {
  Model,
  ModelType,
  ModelProvider,
  CostTier,
  ScrapeRequest,
  PageAction,
  OutputField,
  ActionType,
} from "@/types";
import { MODEL_TO_PROVIDER, PROVIDER_KEY_VENDORS, PROVIDER_NAMES } from "@/types";
import { useI18n } from "@/lib/i18n-context";

interface ScraperFormProps {
  models: Model[];
  isLoading: boolean;
  onSubmit: (request: ScrapeRequest) => void;
}

export function ScraperForm({ models, isLoading, onSubmit }: ScraperFormProps) {
  const { t, tOr } = useI18n();
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState<ModelType>("openai/gpt-oss-120b");
  const [apiKey, setApiKey] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  // New options. `stealth_mode` keeps its API name; what it toggles is a
  // regular desktop browser profile (headers, viewport) for Playwright.
  const [stealthMode, setStealthMode] = useState(true);
  const [useMarkdown, setUseMarkdown] = useState(true);
  const [costTier, setCostTier] = useState<CostTier | "">("");

  // Advanced options
  const [useCache, setUseCache] = useState(true);
  const [actions, setActions] = useState<PageAction[]>([]);
  const [outputFields, setOutputFields] = useState<OutputField[]>([]);

  // Temp state for adding new action
  const [newAction, setNewAction] = useState<PageAction>({
    action: "click",
    selector: "",
    value: "",
    wait_ms: 1000,
  });

  // Temp state for adding new field
  const [newField, setNewField] = useState<OutputField>({
    name: "",
    type: "string",
    description: "",
    required: true,
  });

  // Get current provider from selected model
  const currentProvider: ModelProvider = MODEL_TO_PROVIDER[model] || "groq";
  const isGroq = currentProvider === "groq";

  // Group models by provider
  const modelsByProvider = useMemo(() => {
    const grouped: Record<string, Model[]> = {};
    models.forEach((m) => {
      const provider = m.provider || "other";
      if (!grouped[provider]) {
        grouped[provider] = [];
      }
      grouped[provider].push(m);
    });
    return grouped;
  }, [models]);

  // Get selected model info
  const selectedModel = useMemo(() => {
    return models.find((m) => m.id === model);
  }, [models, model]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!url || !prompt) return;

    const request: ScrapeRequest = {
      url,
      prompt,
      model,
      api_key: apiKey || undefined,
      use_cache: useCache,
      stealth_mode: stealthMode,
      use_markdown: useMarkdown,
    };

    if (costTier) {
      request.cost_tier = costTier;
    }

    if (actions.length > 0) {
      request.actions = actions;
    }

    if (outputFields.length > 0) {
      request.output_schema = outputFields;
    }

    onSubmit(request);
  };

  const addAction = () => {
    if (newAction.action === "click" || newAction.action === "type") {
      if (!newAction.selector) return;
    }
    setActions([...actions, { ...newAction }]);
    setNewAction({ action: "click", selector: "", value: "", wait_ms: 1000 });
  };

  const removeAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const addField = () => {
    if (!newField.name) return;
    setOutputFields([...outputFields, { ...newField }]);
    setNewField({ name: "", type: "string", description: "", required: true });
  };

  const removeField = (index: number) => {
    setOutputFields(outputFields.filter((_, i) => i !== index));
  };

  // Groq doesn't require API key (server may have default)
  const isValid = url.trim() !== "" && prompt.trim() !== "";

  // Provider order: Groq first
  const providerOrder: ModelProvider[] = ["groq", "deepseek", "gemini", "openai", "anthropic", "grok"];

  return (
    <Card className="border-border/50">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl">{t("form.title")}</CardTitle>
        <CardDescription>
          {t("form.description")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Model Selection */}
          <div className="space-y-2">
            <Label htmlFor="model">{t("form.model")}</Label>
            <Select value={model} onValueChange={(v) => setModel(v as ModelType)}>
              <SelectTrigger id="model">
                <SelectValue placeholder={t("form.modelPlaceholder")} />
              </SelectTrigger>
              <SelectContent>
                {providerOrder.map((provider) => {
                  const providerModels = modelsByProvider[provider];
                  if (!providerModels || providerModels.length === 0) return null;

                  return (
                    <SelectGroup key={provider}>
                      <SelectLabel className="text-xs uppercase tracking-wider text-muted-foreground">
                        {provider === "groq" ? t("provider.groq") : PROVIDER_NAMES[provider]}
                      </SelectLabel>
                      {providerModels.map((m) => (
                        <SelectItem key={m.id} value={m.id}>
                          <span className="flex items-center gap-2">
                            <span className="font-medium">{m.name}</span>
                            <span className="text-xs text-muted-foreground">
                              ${m.input_price}/{m.output_price}
                            </span>
                            <Badge
                              variant={
                                m.tier === "free"
                                  ? "default"
                                  : m.tier === "budget"
                                  ? "secondary"
                                  : m.tier === "premium"
                                  ? "default"
                                  : "outline"
                              }
                              className="text-[10px] px-1"
                            >
                              {t(`tier.${m.tier}`)}
                            </Badge>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectGroup>
                  );
                })}
              </SelectContent>
            </Select>
            {selectedModel && (
              <p className="text-xs text-muted-foreground">
                {tOr(`model.${selectedModel.id}`, selectedModel.description)}
              </p>
            )}
          </div>

          {/* API Key: Groq has shared free fallback; other providers need BYOK */}
          {isGroq ? (
            <div className="space-y-2">
              <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3">
                <p className="text-sm font-medium text-emerald-800">
                  {t("form.shared.title")}
                </p>
                {/* The session limit applies to every key, so this no longer
                    promises "unlimited use" with your own key. */}
                <p className="text-xs text-emerald-700 mt-1">
                  {t("form.shared.body")} (
                  <a
                    href="https://console.groq.com/keys"
                    target="_blank"
                    rel="noreferrer noopener"
                    className="underline"
                  >
                    {t("form.shared.link")}
                  </a>
                  ).
                </p>
              </div>
              <Label htmlFor="api-key" className="text-xs text-muted-foreground">
                {t("form.ownKeyLabel")}
              </Label>
              <Input
                id="api-key"
                type="password"
                autoComplete="off"
                placeholder={t("form.ownKeyPlaceholder")}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="font-mono text-sm"
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="api-key">
                {t("form.keyLabel", { provider: PROVIDER_KEY_VENDORS[currentProvider] })}
                <span className="ml-1 rounded-full bg-amber-100 text-amber-700 px-1.5 py-0.5 text-[10px] font-medium align-middle">
                  {t("form.byokRequired")}
                </span>
              </Label>
              <Input
                id="api-key"
                type="password"
                autoComplete="off"
                placeholder={currentProvider === "openai" ? "sk-..." : t("form.keyPlaceholder")}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="font-mono text-sm"
                required
              />
              <p className="text-xs text-muted-foreground">
                {t("form.byokHint")}
              </p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="url">{t("form.url")}</Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="prompt">{t("form.prompt")}</Label>
            <Textarea
              id="prompt"
              placeholder={t("form.promptPlaceholder")}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              required
            />
          </div>

          {/* Optimization Options */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="stealth-mode"
                checked={stealthMode}
                onChange={(e) => setStealthMode(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="stealth-mode" className="text-sm font-normal cursor-pointer">
                {t("form.opt.profile")}
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="use-markdown"
                checked={useMarkdown}
                onChange={(e) => setUseMarkdown(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="use-markdown" className="text-sm font-normal cursor-pointer">
                {t("form.opt.markdown")}
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="use-cache"
                checked={useCache}
                onChange={(e) => setUseCache(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="use-cache" className="text-sm font-normal cursor-pointer">
                {t("form.opt.cache")}
              </Label>
            </div>
          </div>

          {/* Advanced Options Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            {showAdvanced ? t("form.advanced.hide") : t("form.advanced.show")}
            <span className="text-xs">
              {(actions.length > 0 || outputFields.length > 0) &&
                t("form.advanced.count", { actions: actions.length, fields: outputFields.length })}
            </span>
          </button>

          {showAdvanced && (
            <div className="space-y-6 pt-4 border-t border-border/50">
              {/* Smart Routing by Cost Tier */}
              <div className="space-y-2">
                <Label className="text-sm font-semibold">{t("form.routing.label")}</Label>
                <Select
                  // Radix Select rejects empty string as a value (used internally
                  // to represent "no selection"). Map our "" sentinel to the
                  // explicit "use-selected" token at the UI layer; convert back
                  // when persisting / submitting.
                  value={costTier === "" ? "use-selected" : costTier}
                  onValueChange={(v) =>
                    setCostTier(v === "use-selected" ? "" : (v as CostTier))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t("form.routing.placeholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="use-selected">{t("form.routing.selected")}</SelectItem>
                    <SelectItem value="free">{t("form.routing.free")}</SelectItem>
                    <SelectItem value="budget">{t("form.routing.budget")}</SelectItem>
                    <SelectItem value="standard">{t("form.routing.standard")}</SelectItem>
                    <SelectItem value="premium">{t("form.routing.premium")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Page Actions */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold">{t("form.actions.label")}</Label>
                <p className="text-xs text-muted-foreground">
                  {t("form.actions.hint")}
                </p>

                {actions.length > 0 && (
                  <div className="space-y-2">
                    {actions.map((action, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 text-sm bg-muted/50 p-2 rounded"
                      >
                        <Badge variant="outline">{t(`action.${action.action}`)}</Badge>
                        {action.selector && (
                          <code className="text-xs bg-background px-1 rounded">
                            {action.selector}
                          </code>
                        )}
                        {action.value && (
                          <span className="text-muted-foreground">= {action.value}</span>
                        )}
                        <button
                          type="button"
                          onClick={() => removeAction(index)}
                          className="ml-auto text-destructive hover:underline text-xs"
                        >
                          {t("form.remove")}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
                  <Select
                    value={newAction.action}
                    onValueChange={(v) =>
                      setNewAction({ ...newAction, action: v as ActionType })
                    }
                  >
                    <SelectTrigger className="text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="click">{t("action.click")}</SelectItem>
                      <SelectItem value="scroll">{t("action.scroll")}</SelectItem>
                      <SelectItem value="wait">{t("action.wait")}</SelectItem>
                      <SelectItem value="type">{t("action.type")}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder={t("form.selector")}
                    value={newAction.selector || ""}
                    onChange={(e) =>
                      setNewAction({ ...newAction, selector: e.target.value })
                    }
                    className="text-xs"
                  />
                  <Input
                    placeholder={newAction.action === "scroll" ? "down/up" : t("form.value")}
                    value={newAction.value || ""}
                    onChange={(e) =>
                      setNewAction({ ...newAction, value: e.target.value })
                    }
                    className="text-xs"
                  />
                  <Button type="button" variant="outline" size="sm" onClick={addAction}>
                    {t("form.add")}
                  </Button>
                </div>
              </div>

              {/* Output Schema */}
              <div className="space-y-3">
                <Label className="text-sm font-semibold">{t("form.schema.label")}</Label>
                <p className="text-xs text-muted-foreground">
                  {t("form.schema.hint")}
                </p>

                {outputFields.length > 0 && (
                  <div className="space-y-2">
                    {outputFields.map((field, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 text-sm bg-muted/50 p-2 rounded"
                      >
                        <code className="font-semibold">{field.name}</code>
                        <Badge variant="secondary" className="text-xs">
                          {field.type}
                        </Badge>
                        {field.required && (
                          <Badge variant="destructive" className="text-xs">
                            {t("form.field.required")}
                          </Badge>
                        )}
                        {field.description && (
                          <span className="text-xs text-muted-foreground truncate max-w-32">
                            {field.description}
                          </span>
                        )}
                        <button
                          type="button"
                          onClick={() => removeField(index)}
                          className="ml-auto text-destructive hover:underline text-xs"
                        >
                          {t("form.remove")}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2">
                  <Input
                    placeholder={t("form.field.name")}
                    value={newField.name}
                    onChange={(e) => setNewField({ ...newField, name: e.target.value })}
                    className="text-xs"
                  />
                  <Select
                    value={newField.type}
                    onValueChange={(v) =>
                      setNewField({
                        ...newField,
                        type: v as OutputField["type"],
                      })
                    }
                  >
                    <SelectTrigger className="text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="string">string</SelectItem>
                      <SelectItem value="number">number</SelectItem>
                      <SelectItem value="boolean">boolean</SelectItem>
                      <SelectItem value="array">array</SelectItem>
                      <SelectItem value="object">object</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder={t("form.field.desc")}
                    value={newField.description || ""}
                    onChange={(e) =>
                      setNewField({ ...newField, description: e.target.value })
                    }
                    className="text-xs"
                  />
                  <div className="flex items-center gap-1">
                    <input
                      type="checkbox"
                      checked={newField.required}
                      onChange={(e) =>
                        setNewField({ ...newField, required: e.target.checked })
                      }
                      className="rounded"
                    />
                    <span className="text-xs">{t("form.field.req")}</span>
                  </div>
                  <Button type="button" variant="outline" size="sm" onClick={addField}>
                    {t("form.add")}
                  </Button>
                </div>
              </div>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={!isValid || isLoading}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <LoadingSpinner />
                {t("form.submitting")}
              </span>
            ) : (
              t("form.submit")
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function LoadingSpinner() {
  return (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
