const translations: Record<string, Record<string, string>> = {
  en: {
    'nav.title': 'AI Web Scraper',
    'badge': 'AI-Powered Web Scraping',
    'hero.title1': 'Intelligent',
    'hero.title2': 'Web Scraper',
    'hero.subtitle': 'Extract structured data from any website using artificial intelligence. Just provide the URL, describe what you want to extract, and choose your AI model.',
    'pipeline.label': 'How It Works',
    'pipeline.step': 'Step',
    'pipeline.1.title': 'Headless Rendering',
    'pipeline.1.desc': 'Playwright launches a stealth Chromium browser that renders JavaScript-heavy pages, bypasses bot detection, and captures the fully-loaded DOM.',
    'pipeline.2.title': 'Smart Cleanup',
    'pipeline.2.desc': 'Strips navigation, ads, scripts and boilerplate. Converts raw HTML to clean Markdown, reducing token usage by up to 67%.',
    'pipeline.3.title': 'LLM Extraction',
    'pipeline.3.desc': 'Sends the cleaned content to your chosen AI model with your prompt. The model extracts exactly the structured data you described.',
    'pipeline.4.title': 'Structured Output',
    'pipeline.4.desc': 'Returns the extracted data as clean JSON or Markdown, ready for your pipeline. Handles pagination, tables, and nested structures.',
    'tech.stealth': 'Stealth Mode (anti-detection)',
    'tech.models': '5 models: OpenAI, DeepSeek, Gemini, Claude, Grok',
    'tech.tokens': '67% token reduction',
    'tech.rate': 'Session-based rate limiting',
    'tryit.label': 'Try It',
    'footer.built': 'Built with',
    'footer.tech': 'Multi-Provider AI -- Headless Chromium -- Token Optimization -- Stealth Mode',
  },
  pt: {
    'nav.title': 'AI Web Scraper',
    'badge': 'Web Scraping com IA',
    'hero.title1': 'Web Scraper',
    'hero.title2': 'Inteligente',
    'hero.subtitle': 'Extraia dados estruturados de qualquer site usando inteligencia artificial. Forneca a URL, descreva o que deseja extrair e escolha seu modelo de IA.',
    'pipeline.label': 'Como Funciona',
    'pipeline.step': 'Etapa',
    'pipeline.1.title': 'Renderizacao Headless',
    'pipeline.1.desc': 'O Playwright abre um navegador Chromium stealth que renderiza paginas com JavaScript, bypassa deteccao de bots e captura o DOM completo.',
    'pipeline.2.title': 'Limpeza Inteligente',
    'pipeline.2.desc': 'Remove navegacao, anuncios, scripts e boilerplate. Converte HTML bruto em Markdown limpo, reduzindo uso de tokens em ate 67%.',
    'pipeline.3.title': 'Extracao com LLM',
    'pipeline.3.desc': 'Envia o conteudo limpo para o modelo de IA escolhido com seu prompt. O modelo extrai exatamente os dados estruturados que voce descreveu.',
    'pipeline.4.title': 'Saida Estruturada',
    'pipeline.4.desc': 'Retorna os dados extraidos como JSON ou Markdown limpo, pronto para seu pipeline. Lida com paginacao, tabelas e estruturas aninhadas.',
    'tech.stealth': 'Modo Stealth (anti-deteccao)',
    'tech.models': '5 modelos: OpenAI, DeepSeek, Gemini, Claude, Grok',
    'tech.tokens': '67% reducao de tokens',
    'tech.rate': 'Rate limiting por sessao',
    'tryit.label': 'Experimente',
    'footer.built': 'Feito com',
    'footer.tech': 'IA Multi-Provedor -- Chromium Headless -- Otimizacao de Tokens -- Modo Stealth',
  },
};

export type Locale = 'en' | 'pt';

export function detectLocale(): Locale {
  if (typeof window === 'undefined') return 'en';
  const lang = navigator.language.toLowerCase();
  if (lang.startsWith('pt')) return 'pt';
  return 'en';
}

export function getTranslations(locale: Locale) {
  const dict = translations[locale] || translations.en;
  return (key: string): string => dict[key] || translations.en[key] || key;
}
