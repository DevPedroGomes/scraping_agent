"use client";

import { Scraper } from "@/components/scraper";
import { Globe, Code2, Cpu, FileJson, Shield } from "lucide-react";
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

      <div className="max-w-6xl mx-auto px-6 sm:px-8 py-16">
        {/* Hero */}
        <header className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-100 text-xs font-medium font-mono mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            {t('badge')}
          </div>

          <h1 className="text-5xl md:text-6xl font-semibold tracking-tighter leading-[0.9] text-neutral-900 mb-6">
            {t('hero.title1')}
            <br />
            <span className="text-emerald-600">{t('hero.title2')}</span>
          </h1>

          <p className="text-lg text-neutral-500 leading-relaxed max-w-2xl mx-auto">
            {t('hero.subtitle')}
          </p>
        </header>

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
        <footer className="border-t border-neutral-200 mt-16 pt-8 pb-8 text-center">
          <div className="space-y-2">
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
        </footer>
      </div>
    </main>
  );
}
