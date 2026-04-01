import { Scraper } from "@/components/scraper";
import { Globe, Code2, Cpu, FileJson, Shield } from "lucide-react";

const pipelineSteps = [
  {
    icon: Globe,
    title: "Headless Rendering",
    description: "Playwright launches a stealth Chromium browser that renders JavaScript-heavy pages, bypasses bot detection, and captures the fully-loaded DOM.",
    color: "bg-blue-50 text-blue-600",
  },
  {
    icon: Code2,
    title: "Smart Cleanup",
    description: "Strips navigation, ads, scripts and boilerplate. Converts raw HTML to clean Markdown, reducing token usage by up to 67%.",
    color: "bg-purple-50 text-purple-600",
  },
  {
    icon: Cpu,
    title: "LLM Extraction",
    description: "Sends the cleaned content to your chosen AI model with your prompt. The model extracts exactly the structured data you described.",
    color: "bg-emerald-50 text-emerald-600",
  },
  {
    icon: FileJson,
    title: "Structured Output",
    description: "Returns the extracted data as clean JSON or Markdown, ready for your pipeline. Handles pagination, tables, and nested structures.",
    color: "bg-orange-50 text-orange-600",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-neutral-200 bg-white/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto flex h-14 items-center px-6 sm:px-8">
          <div className="flex items-center gap-2.5">
            <img src="/logo.png" alt="Logo" className="h-8 w-8 rounded-lg object-cover" />
            <span className="font-semibold tracking-tight text-neutral-900">AI Web Scraper</span>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 sm:px-8 py-16">
        {/* Hero */}
        <header className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-100 text-xs font-medium font-mono mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            AI-Powered Web Scraping
          </div>

          <h1 className="text-5xl md:text-6xl font-semibold tracking-tighter leading-[0.9] text-neutral-900 mb-6">
            Intelligent
            <br />
            <span className="text-emerald-600">Web Scraper</span>
          </h1>

          <p className="text-lg text-neutral-500 leading-relaxed max-w-2xl mx-auto">
            Extract structured data from any website using artificial intelligence.
            Just provide the URL, describe what you want to extract, and choose your AI model.
          </p>
        </header>

        {/* Pipeline */}
        <section className="mb-16">
          <div className="flex items-center gap-4 mb-6">
            <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest font-mono">How It Works</span>
            <div className="h-px flex-1 bg-neutral-200" />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {pipelineSteps.map((step, i) => (
              <div key={step.title} className="bg-white border border-neutral-200 rounded-2xl p-5 hover-lift">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`rounded-xl p-2 ${step.color}`}>
                    <step.icon className="h-4 w-4" />
                  </div>
                  <span className="text-xs font-mono text-neutral-400">Step {i + 1}</span>
                </div>
                <h3 className="font-semibold text-neutral-900 text-sm mb-1">{step.title}</h3>
                <p className="text-xs text-neutral-500 leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-neutral-400 font-mono">
            <span className="flex items-center gap-1.5">
              <Shield className="h-3.5 w-3.5" />
              Stealth Mode (anti-detection)
            </span>
            <span>5 models: OpenAI · DeepSeek · Gemini · Claude · Grok</span>
            <span>67% token reduction</span>
            <span>Session-based rate limiting</span>
          </div>
        </section>

        {/* Scraper Component */}
        <section>
          <div className="flex items-center gap-4 mb-6">
            <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest font-mono">Try It</span>
            <div className="h-px flex-1 bg-neutral-200" />
          </div>

          <Scraper />
        </section>

        {/* Footer */}
        <footer className="border-t border-neutral-200 mt-16 pt-8 pb-8 text-center">
          <div className="space-y-2">
            <p className="text-sm text-neutral-500">
              Built with{" "}
              <span className="font-medium text-neutral-900">Next.js</span>,{" "}
              <span className="font-medium text-neutral-900">FastAPI</span> and{" "}
              <span className="font-medium text-neutral-900">Playwright</span>
            </p>
            <p className="text-xs text-neutral-400 font-mono">
              Multi-Provider AI · Headless Chromium · Token Optimization · Stealth Mode
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
