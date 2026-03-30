import { Scraper } from "@/components/scraper";

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
            Just provide the URL and describe what you want to extract.
          </p>
        </header>

        <Scraper />

        <footer className="border-t border-neutral-200 mt-16 pt-8 pb-8 text-center">
          <div className="space-y-2">
            <p className="text-sm text-neutral-500">
              Built with{" "}
              <span className="font-medium text-neutral-900">Next.js</span>,{" "}
              <span className="font-medium text-neutral-900">FastAPI</span> and{" "}
              <span className="font-medium text-neutral-900">Playwright</span>
            </p>
            <p className="text-xs text-neutral-400 font-mono">
              Multi-Provider AI (OpenAI, DeepSeek, Gemini, Claude, Grok) | 67% Token Reduction | Stealth Mode
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
