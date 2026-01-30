import { Scraper } from "@/components/scraper";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-background/95">
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            AI-Powered Web Scraping
          </div>

          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Intelligent
            <span className="text-primary"> Web Scraper</span>
          </h1>

          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Extract structured data from any website using artificial intelligence.
            Just provide the URL and describe what you want to extract.
          </p>
        </header>

        <Scraper />

        <footer className="mt-16 text-center text-sm text-muted-foreground">
          <div className="space-y-2">
            <p>
              Built with{" "}
              <span className="font-medium text-foreground">Next.js</span>,{" "}
              <span className="font-medium text-foreground">FastAPI</span> and{" "}
              <span className="font-medium text-foreground">Playwright</span>
            </p>
            <p className="text-xs">
              Multi-Provider AI (OpenAI, DeepSeek, Gemini, Claude, Grok) | 67% Token Reduction | Stealth Mode
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
