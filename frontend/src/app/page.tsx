"use client";

import { Scraper } from "@/components/scraper";
import { Globe, Code2, Cpu, FileJson, Shield, ShieldCheck, Lock, Database, Zap, KeyRound, ArrowRight } from "lucide-react";
import { useLocale } from "@/hooks/use-locale";
import { getTranslations } from "@/lib/i18n";

export default function Home() {
  const { locale, changeLocale } = useLocale();
  const t = getTranslations(locale);

  const pipelineSteps = [
    {
      icon: Globe,
      title: t('pipeline.1.title'),
      description: t('pipeline.1.desc'),
      color: "bg-blue-50 text-blue-600",
    },
    {
      icon: Code2,
      title: t('pipeline.2.title'),
      description: t('pipeline.2.desc'),
      color: "bg-purple-50 text-purple-600",
    },
    {
      icon: Cpu,
      title: t('pipeline.3.title'),
      description: t('pipeline.3.desc'),
      color: "bg-emerald-50 text-emerald-600",
    },
    {
      icon: FileJson,
      title: t('pipeline.4.title'),
      description: t('pipeline.4.desc'),
      color: "bg-orange-50 text-orange-600",
    },
  ];

  return (
    <main className="min-h-screen bg-white">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-neutral-200 bg-white/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto flex h-14 items-center px-6 sm:px-8">
          <div className="flex items-center gap-2.5">
            <img src="/logo.png" alt="Logo" className="h-8 w-8 rounded-lg object-cover" />
            <span className="font-semibold tracking-tight text-neutral-900">{t('nav.title')}</span>
          </div>
          <div className="ml-auto flex items-center gap-1 text-xs font-mono">
            <button
              onClick={() => changeLocale('en')}
              className={`px-2 py-1 rounded transition-colors ${locale === 'en' ? 'text-neutral-900 font-semibold' : 'text-neutral-400 hover:text-neutral-600'}`}
            >
              EN
            </button>
            <span className="text-neutral-300">|</span>
            <button
              onClick={() => changeLocale('pt')}
              className={`px-2 py-1 rounded transition-colors ${locale === 'pt' ? 'text-neutral-900 font-semibold' : 'text-neutral-400 hover:text-neutral-600'}`}
            >
              PT
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 -z-10 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(16,185,129,0.10), transparent 60%), radial-gradient(ellipse 50% 35% at 85% 30%, rgba(59,130,246,0.07), transparent 70%)",
          }}
        />
        <div className="max-w-5xl mx-auto px-6 sm:px-8 pt-16 pb-12 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-emerald-200 text-xs font-medium font-mono mb-6 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-emerald-700">Production-ready · BYOK 6 providers</span>
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-semibold tracking-tighter leading-[0.9] text-neutral-900 mb-6">
            URL + a sentence
            <br />
            <span className="bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">becomes JSON.</span>
          </h1>

          <p className="text-lg text-neutral-500 leading-relaxed max-w-2xl mx-auto mb-3">
            {t('hero.subtitle')}
          </p>
          <p className="text-sm text-neutral-400 font-mono max-w-xl mx-auto">
            With actual SSRF defense, DNS-rebinding guards and prompt-injection isolation.
          </p>

          {/* Quick visual: URL → JSON */}
          <div className="mt-10 max-w-3xl mx-auto grid sm:grid-cols-3 items-center gap-3">
            <div className="bg-white border border-neutral-200 rounded-xl p-3 text-left text-xs font-mono">
              <p className="text-[10px] text-neutral-400 uppercase mb-1">Input</p>
              <p className="text-neutral-700 truncate">https://news.ycombinator.com</p>
              <p className="text-neutral-500 mt-1">&quot;top 5 story titles&quot;</p>
            </div>
            <div className="hidden sm:flex justify-center">
              <ArrowRight className="h-5 w-5 text-neutral-300" />
            </div>
            <div className="bg-neutral-900 text-emerald-400 rounded-xl p-3 text-left text-xs font-mono shadow-lg">
              <p className="text-[10px] text-neutral-500 uppercase mb-1">Output</p>
              <pre className="text-[10px] leading-relaxed overflow-hidden">{`[
  { "title": "Show HN: ..." },
  { "title": "Ask HN: ..." },
  ...
]`}</pre>
            </div>
          </div>
        </div>
      </section>

      {/* Security pillars */}
      <section className="max-w-6xl mx-auto px-6 sm:px-8 py-12">
        <div className="text-center mb-10">
          <span className="text-xs uppercase tracking-widest text-neutral-400 font-mono">Engineered for production</span>
          <h2 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900 mt-2">
            What separates this from a 30-line script
          </h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: ShieldCheck, label: "SSRF v2", desc: "IDNA + IPv6 unwrap + IP allowlist computed before the request, re-checked on every subresource." },
            { icon: Shield,      label: "DNS-rebinding guard", desc: "Playwright route hooks intercept each subresource and abort if it leaves the allow-set." },
            { icon: Lock,        label: "Prompt injection cage", desc: "Untrusted scraped content is wrapped in a system-prompt isolation layer before reaching the LLM." },
            { icon: KeyRound,    label: "Per-key cache scoping", desc: "Cache key includes sha256 of API key — no cross-user leakage between BYOK sessions." },
          ].map((p) => (
            <div key={p.label} className="bg-white border border-neutral-200 rounded-2xl p-5 hover-lift">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
                <p.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-neutral-900 text-sm mb-1.5">{p.label}</h3>
              <p className="text-xs text-neutral-500 leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-6 sm:px-8 py-4">

        {/* Pipeline */}
        <section className="mb-16">
          <div className="flex items-center gap-4 mb-6">
            <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest font-mono">{t('pipeline.label')}</span>
            <div className="h-px flex-1 bg-neutral-200" />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {pipelineSteps.map((step, i) => (
              <div key={i} className="bg-white border border-neutral-200 rounded-2xl p-5 hover-lift">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`rounded-xl p-2 ${step.color}`}>
                    <step.icon className="h-4 w-4" />
                  </div>
                  <span className="text-xs font-mono text-neutral-400">{t('pipeline.step')} {i + 1}</span>
                </div>
                <h3 className="font-semibold text-neutral-900 text-sm mb-1">{step.title}</h3>
                <p className="text-xs text-neutral-500 leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-neutral-400 font-mono">
            <span className="flex items-center gap-1.5">
              <Shield className="h-3.5 w-3.5" />
              {t('tech.stealth')}
            </span>
            <span>{t('tech.models')}</span>
            <span>{t('tech.tokens')}</span>
            <span>{t('tech.rate')}</span>
          </div>
        </section>

        {/* Scraper Component */}
        <section>
          <div className="flex items-center gap-4 mb-6">
            <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest font-mono">{t('tryit.label')}</span>
            <div className="h-px flex-1 bg-neutral-200" />
          </div>

          <Scraper />
        </section>

        {/* Footer */}
        <footer className="border-t border-neutral-200 mt-16 pt-8 pb-8">
          <div className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:text-left">
            <div className="space-y-1">
              <p className="text-sm text-neutral-500">
                {t('footer.built')}{" "}
                <span className="font-medium text-neutral-900">Next.js</span>,{" "}
                <span className="font-medium text-neutral-900">FastAPI</span> and{" "}
                <span className="font-medium text-neutral-900">Playwright</span>
              </p>
              <p className="text-xs text-neutral-400 font-mono">
                {t('footer.tech')}
              </p>
            </div>
            <div className="flex items-center gap-4 text-sm text-neutral-500">
              <a href="https://github.com/devpedrogomes" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-900 transition-colors">GitHub</a>
              <a href="https://www.linkedin.com/in/devpgomes" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-900 transition-colors">LinkedIn</a>
              <a href="https://pgdev.com.br" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-900 transition-colors">Portfolio</a>
            </div>
          </div>
        </footer>
      </div>
    </main>
  );
}
