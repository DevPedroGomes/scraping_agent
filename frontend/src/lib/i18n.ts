// Every string the visitor can see lives here, in both languages. Before this,
// only the landing copy was translated: with PT selected the form, buttons,
// result panel, toasts and errors stayed in English, and the footer read
// "Feito com Next.js, FastAPI and Playwright".
//
// Model descriptions and sample names come from the API in English; the `pt`
// dictionary overrides them by id (see `tOr`), and English falls back to the
// API text so a new model never shows a raw key.

type Dict = Record<string, string>;

const en: Dict = {
  'meta.title': 'AI Web Scraper: a URL and a sentence become structured JSON',
  'nav.title': 'AI Web Scraper',
  'nav.logoAlt': 'AI Web Scraper logo',

  'hero.badge': 'Production-ready · BYOK {providers} providers',
  'hero.title1': 'URL + a sentence',
  'hero.title2': 'becomes JSON.',
  'hero.subtitle': 'Extract structured data from any public website using artificial intelligence. Just provide the URL, describe what you want to extract, and choose your AI model.',
  'hero.security': 'With actual SSRF defense, DNS-rebinding guards and prompt-injection isolation.',
  'hero.input': 'Input',
  'hero.output': 'Output',
  'hero.samplePrompt': '"top 5 story titles"',

  'pillars.label': 'Engineered for production',
  'pillars.title': 'What separates this from a 30-line script',
  'pillars.ssrf.title': 'SSRF v2',
  'pillars.ssrf.desc': 'IDNA + IPv6 unwrap + IP allowlist computed before the request, re-checked on every subresource.',
  'pillars.dns.title': 'DNS-rebinding guard',
  'pillars.dns.desc': 'Playwright route hooks intercept each subresource and abort if it leaves the allow-set.',
  'pillars.injection.title': 'Prompt injection cage',
  'pillars.injection.desc': 'Untrusted scraped content is wrapped in a system-prompt isolation layer before reaching the LLM.',
  'pillars.cache.title': 'Per-key cache scoping',
  'pillars.cache.desc': 'Cache key includes sha256 of API key, no cross-user leakage between BYOK sessions.',

  'pipeline.label': 'How It Works',
  'pipeline.step': 'Step',
  'pipeline.1.title': 'Headless Rendering',
  'pipeline.1.desc': 'Playwright opens a headless Chromium with a regular desktop browser profile, renders JavaScript-heavy pages and captures the fully loaded DOM.',
  'pipeline.2.title': 'Smart Cleanup',
  'pipeline.2.desc': 'Strips navigation, ads, scripts and boilerplate. Converts raw HTML to clean Markdown, reducing token usage by up to 67%.',
  'pipeline.3.title': 'LLM Extraction',
  'pipeline.3.desc': 'Sends the cleaned content to your chosen AI model with your prompt. The model is told to use only what the page states and to return null instead of guessing.',
  'pipeline.4.title': 'Structured Output',
  'pipeline.4.desc': 'Returns the extracted data as JSON. Define an output schema and required fields and types are checked; without one, the result is labeled as not validated.',
  'tech.profile': 'Realistic browser profile',
  'tech.models': '{models} models from {providers} providers',
  'tech.tokens': 'Up to 67% fewer tokens',
  'tech.rate': 'Session-based rate limiting',
  'tryit.label': 'Try It',

  'footer.built': 'Built with',
  'footer.and': 'and',
  'footer.tech': 'Multi-provider AI · Headless Chromium · Token optimization · Realistic browser profile',
  'footer.portfolio': 'Portfolio',

  'samples.label': 'Pre-recorded samples (free, no live scrape):',
  'samples.badge': 'SAMPLE',

  'form.title': 'Extract Data',
  'form.description': 'Enter the URL and describe what you want to extract',
  'form.model': 'AI Model',
  'form.modelPlaceholder': 'Select a model',
  'form.shared.title': '✓ Free showcase mode, using a shared Groq key',
  'form.shared.body': 'No key needed; limited per session and per day. Your own free Groq key skips the shared daily cap',
  'form.shared.link': 'get one in 30s',
  'form.ownKeyLabel': 'Optional: your own Groq API key',
  'form.ownKeyPlaceholder': 'gsk_... (leave blank to use shared free mode)',
  'form.keyLabel': '{provider} API key',
  'form.byokRequired': 'BYOK required',
  'form.keyPlaceholder': 'Enter API key...',
  'form.byokHint': 'Paid models need your own key. Not stored, used only for this request. Pick a Groq model above for the free shared mode.',
  'form.url': 'Website URL',
  'form.prompt': 'What do you want to extract?',
  'form.promptPlaceholder': 'E.g., Extract all article titles and their summaries...',
  'form.opt.profile': 'Realistic browser profile',
  'form.opt.markdown': 'Markdown (~67% cheaper)',
  'form.opt.cache': 'Use cache',
  'form.advanced.show': 'Show advanced options',
  'form.advanced.hide': 'Hide advanced options',
  'form.advanced.count': '({actions} actions, {fields} fields)',
  'form.routing.label': 'Cost-tier routing (auto-select model)',
  'form.routing.placeholder': 'Use selected model above',
  'form.routing.selected': 'Use selected model',
  'form.routing.free': 'Free (open-weight models on Groq)',
  'form.routing.budget': 'Budget (cheapest)',
  'form.routing.standard': 'Standard (balanced)',
  'form.routing.premium': 'Premium (best quality)',
  'form.actions.label': 'Page actions (before scraping)',
  'form.actions.hint': 'Execute actions like clicking buttons or scrolling before extracting data',
  'form.selector': 'CSS selector',
  'form.value': 'value',
  'form.add': 'Add',
  'form.remove': 'Remove',
  'form.schema.label': 'Output schema (validated output)',
  'form.schema.hint': 'Define the expected fields. The result is checked for required fields and types, and fields the page does not state come back as null.',
  'form.field.name': 'Field name',
  'form.field.desc': 'Description',
  'form.field.req': 'Req',
  'form.field.required': 'required',
  'form.submit': 'Start Scraping',
  'form.submitting': 'Extracting data...',

  'action.click': 'Click',
  'action.scroll': 'Scroll',
  'action.wait': 'Wait',
  'action.type': 'Type',

  'tier.free': 'free',
  'tier.budget': 'budget',
  'tier.standard': 'standard',
  'tier.premium': 'premium',

  'provider.groq': 'Groq (free)',

  'result.title': 'Result',
  'result.emptyDesc': 'Extracted data will appear here',
  'result.emptyBody': 'No results yet. Make a request to start.',
  'result.errorDesc': 'An error occurred',
  'result.clear': 'Clear',
  'result.success': 'Success',
  'result.error': 'Error',
  'result.sampleDesc': 'Pre-recorded sample, not a live scrape',
  'result.executed': 'Executed in {seconds}s',
  'result.using': ' using {model}',
  'result.validationErrors': 'Validation errors:',
  'result.viewJson': 'JSON result',
  'result.viewMarkdown': 'Processed content',

  'badge.sample': 'Sample',
  'badge.cache': 'Cache hit',
  'badge.truncated': 'Content truncated',
  'badge.tokens': '{n} tokens',
  'badge.actions.one': '1 action executed',
  'badge.actions.other': '{n} actions executed',
  'badge.fetch': 'Fetch: {s}s',
  'badge.parse': 'Parse: {s}s',
  'badge.llm': 'LLM: {s}s',
  'badge.left.one': '1 scrape left',
  'badge.left.other': '{n} scrapes left',

  'validation.passed': 'Schema validated',
  'validation.failed': 'Schema check failed',
  'validation.none': 'No schema validation',
  'validation.noneHint': 'No output schema was defined, so nothing checked this JSON. Add fields under advanced options to validate it.',
  'validation.missing': 'Missing required field: {field}',
  'validation.wrongType': "Field '{field}' has the wrong type. Expected {type}",
  'validation.notFound': "Required field '{field}' was not found on the page (null)",
  'validation.notObject': 'Output is not a JSON object',

  'status.status': 'Status:',
  'status.online': 'Online',
  'status.offline': 'Offline',
  'status.scrapes': 'Scrapes:',
  'status.version': 'Version:',

  'toast.starting': 'Starting data extraction...',
  'toast.success': 'Data extracted successfully',
  'toast.fromCache': ' (from cache)',
  'toast.sample': ' (pre-recorded sample)',

  'error.invalid_url': 'This URL cannot be used. Check that it starts with http:// or https:// and that the domain exists.',
  'error.blocked_url': 'For security, private, internal and cloud-metadata addresses cannot be accessed.',
  'error.api_key_required': 'This model needs your own API key. Pick a Groq model for the free shared mode, or paste your key above.',
  'error.provider_auth': 'The provider rejected the API key. Check the key and try again.',
  'error.provider_unavailable': 'The free shared key is unavailable right now. Paste your own key or try again later.',
  'error.provider_rate_limited': 'The provider is rate limiting requests. Wait a moment or try another model.',
  'error.provider_quota': 'API quota exceeded. Check your account limits.',
  'error.site_timeout': 'The site took too long to respond. Try again.',
  'error.rate_limited': 'Too many requests in a short time. Wait a moment.',
  'error.scrape_limit_reached': 'You used all live scrapes for this session. The samples are still available.',
  'error.daily_limit_reached': 'The free shared key reached its daily limit. Paste your own API key or come back tomorrow.',
  'error.internal_error': 'Could not complete the extraction.',
  'error.internal_error_ref': 'Could not complete the extraction. Reference ID: {ref}',
  'error.session_expired': 'Your demo session expired. A new one was opened; try again.',
  'error.client_timeout': 'The request timed out after 5 minutes. Try again or use a simpler query.',
  'error.network': 'Could not reach the server. Check your connection and try again.',
  'error.unknown': 'Something went wrong. Try again.',

  'session.tooMany': 'Too many demo sessions opened from your network in the last few minutes. Wait about ten minutes and reload.',
  'session.failed': 'Could not open a demo session right now. Reload the page in a moment.',
};

const pt: Dict = {
  'meta.title': 'Web Scraper com IA: uma URL e uma frase viram JSON estruturado',
  'nav.title': 'Web Scraper com IA',
  'nav.logoAlt': 'Logo do Web Scraper com IA',

  'hero.badge': 'Pronto para produção · BYOK em {providers} provedores',
  'hero.title1': 'URL + uma frase',
  'hero.title2': 'vira JSON.',
  'hero.subtitle': 'Extraia dados estruturados de qualquer site público usando inteligência artificial. Forneça a URL, descreva o que deseja extrair e escolha seu modelo de IA.',
  'hero.security': 'Com defesa real contra SSRF, proteção contra DNS rebinding e isolamento de prompt injection.',
  'hero.input': 'Entrada',
  'hero.output': 'Saída',
  'hero.samplePrompt': '"títulos das 5 principais histórias"',

  'pillars.label': 'Feito para produção',
  'pillars.title': 'O que separa isto de um script de 30 linhas',
  'pillars.ssrf.title': 'SSRF v2',
  'pillars.ssrf.desc': 'IDNA + desembrulho de IPv6 + lista de IPs permitidos calculada antes da requisição e reconferida em cada sub-recurso.',
  'pillars.dns.title': 'Proteção contra DNS rebinding',
  'pillars.dns.desc': 'Hooks de rota do Playwright interceptam cada sub-recurso e abortam se ele sair do conjunto de IPs permitidos.',
  'pillars.injection.title': 'Isolamento de prompt injection',
  'pillars.injection.desc': 'O conteúdo raspado, não confiável, é isolado por uma camada no system prompt antes de chegar ao LLM.',
  'pillars.cache.title': 'Cache isolado por chave',
  'pillars.cache.desc': 'A chave do cache inclui o sha256 da chave de API: nada vaza entre sessões BYOK de pessoas diferentes.',

  'pipeline.label': 'Como Funciona',
  'pipeline.step': 'Etapa',
  'pipeline.1.title': 'Renderização Headless',
  'pipeline.1.desc': 'O Playwright abre um Chromium headless com perfil de navegador de desktop comum, renderiza páginas com JavaScript e captura o DOM completo.',
  'pipeline.2.title': 'Limpeza Inteligente',
  'pipeline.2.desc': 'Remove navegação, anúncios, scripts e boilerplate. Converte HTML bruto em Markdown limpo, reduzindo o uso de tokens em até 67%.',
  'pipeline.3.title': 'Extração com LLM',
  'pipeline.3.desc': 'Envia o conteúdo limpo para o modelo de IA escolhido junto com seu prompt. O modelo é instruído a usar só o que a página afirma e a devolver null em vez de chutar.',
  'pipeline.4.title': 'Saída Estruturada',
  'pipeline.4.desc': 'Devolve os dados extraídos em JSON. Com um schema de saída, campos obrigatórios e tipos são conferidos; sem schema, o resultado aparece marcado como não validado.',
  'tech.profile': 'Perfil de navegador realista',
  'tech.models': '{models} modelos de {providers} provedores',
  'tech.tokens': 'Até 67% menos tokens',
  'tech.rate': 'Limite de requisições por sessão',
  'tryit.label': 'Experimente',

  'footer.built': 'Feito com',
  'footer.and': 'e',
  'footer.tech': 'IA multiprovedor · Chromium headless · Otimização de tokens · Perfil de navegador realista',
  'footer.portfolio': 'Portfólio',

  'samples.label': 'Amostras pré-gravadas (grátis, sem scrape ao vivo):',
  'samples.badge': 'AMOSTRA',
  'example.hacker-news': 'Hacker News - principais histórias',
  'example.github-trending': 'GitHub Trending - repositórios em alta',
  'example.product-hunt': 'Product Hunt - destaques do dia',

  'form.title': 'Extrair dados',
  'form.description': 'Informe a URL e descreva o que você quer extrair',
  'form.model': 'Modelo de IA',
  'form.modelPlaceholder': 'Escolha um modelo',
  'form.shared.title': '✓ Modo demonstração gratuito, com uma chave Groq compartilhada',
  'form.shared.body': 'Não precisa de chave; há limite por sessão e por dia. Com sua própria chave gratuita da Groq você não depende do teto diário compartilhado',
  'form.shared.link': 'crie uma em 30s',
  'form.ownKeyLabel': 'Opcional: sua própria chave de API da Groq',
  'form.ownKeyPlaceholder': 'gsk_... (deixe em branco para usar o modo gratuito compartilhado)',
  'form.keyLabel': 'Chave de API: {provider}',
  'form.byokRequired': 'Exige sua chave',
  'form.keyPlaceholder': 'Cole a chave de API...',
  'form.byokHint': 'Modelos pagos exigem sua própria chave. Ela não é armazenada e serve só para esta requisição. Escolha um modelo da Groq acima para o modo gratuito compartilhado.',
  'form.url': 'URL do site',
  'form.prompt': 'O que você quer extrair?',
  'form.promptPlaceholder': 'Ex.: extraia os títulos de todos os artigos e seus resumos...',
  'form.opt.profile': 'Perfil de navegador realista',
  'form.opt.markdown': 'Markdown (~67% mais barato)',
  'form.opt.cache': 'Usar cache',
  'form.advanced.show': 'Mostrar opções avançadas',
  'form.advanced.hide': 'Ocultar opções avançadas',
  'form.advanced.count': '({actions} ações, {fields} campos)',
  'form.routing.label': 'Roteamento por custo (escolhe o modelo)',
  'form.routing.placeholder': 'Usar o modelo escolhido acima',
  'form.routing.selected': 'Usar o modelo escolhido',
  'form.routing.free': 'Grátis (modelos abertos na Groq)',
  'form.routing.budget': 'Econômico (mais barato)',
  'form.routing.standard': 'Padrão (equilibrado)',
  'form.routing.premium': 'Premium (melhor qualidade)',
  'form.actions.label': 'Ações na página (antes da extração)',
  'form.actions.hint': 'Execute ações como clicar em botões ou rolar a página antes de extrair os dados',
  'form.selector': 'Seletor CSS',
  'form.value': 'valor',
  'form.add': 'Adicionar',
  'form.remove': 'Remover',
  'form.schema.label': 'Schema de saída (saída validada)',
  'form.schema.hint': 'Defina os campos esperados. O resultado é conferido quanto a campos obrigatórios e tipos, e campos que a página não informa voltam como null.',
  'form.field.name': 'Nome do campo',
  'form.field.desc': 'Descrição',
  'form.field.req': 'Obrig.',
  'form.field.required': 'obrigatório',
  'form.submit': 'Iniciar extração',
  'form.submitting': 'Extraindo dados...',

  'action.click': 'Clicar',
  'action.scroll': 'Rolar',
  'action.wait': 'Esperar',
  'action.type': 'Digitar',

  'tier.free': 'grátis',
  'tier.budget': 'econômico',
  'tier.standard': 'padrão',
  'tier.premium': 'premium',

  'provider.groq': 'Groq (grátis)',

  'model.openai/gpt-oss-120b': 'Grátis - modelo aberto de 120B servido pela Groq',
  'model.openai/gpt-oss-20b': 'Grátis - rápido, para extrações simples',
  'model.deepseek-chat': 'Melhor custo-benefício - barato e capaz (contexto de 128K)',
  'model.gemini-2.5-flash-lite': 'Muito rápido e barato, com contexto de 1M',
  'model.gemini-2.5-flash': 'Rápido, com janela de contexto de 1M',
  'model.gemini-2.5-pro': 'O modelo Gemini mais capaz',
  'model.gpt-5-nano': 'O modelo mais rápido da OpenAI - bom para tarefas simples',
  'model.gpt-5-mini': 'Equilíbrio entre velocidade e inteligência',
  'model.gpt-5': 'O modelo mais inteligente da OpenAI',
  'model.gpt-4o-mini': 'Rápido e econômico',
  'model.gpt-4o': 'Multimodal',
  'model.claude-haiku-4-5': 'O Claude mais rápido - ótimo para saída estruturada',
  'model.claude-sonnet-4-6': 'Melhor combinação de velocidade e inteligência',
  'model.claude-opus-4-6': 'O modelo mais inteligente para tarefas complexas',
  'model.grok-4-fast-non-reasoning': 'Rápido, com janela de contexto de 2M',
  'model.grok-4-0709': 'O modelo mais capaz da xAI',

  'result.title': 'Resultado',
  'result.emptyDesc': 'Os dados extraídos aparecem aqui',
  'result.emptyBody': 'Nenhum resultado ainda. Faça uma requisição para começar.',
  'result.errorDesc': 'Ocorreu um erro',
  'result.clear': 'Limpar',
  'result.success': 'Sucesso',
  'result.error': 'Erro',
  'result.sampleDesc': 'Amostra pré-gravada, não é um scrape ao vivo',
  'result.executed': 'Executado em {seconds}s',
  'result.using': ' com {model}',
  'result.validationErrors': 'Erros de validação:',
  'result.viewJson': 'Resultado JSON',
  'result.viewMarkdown': 'Conteúdo processado',

  'badge.sample': 'Amostra',
  'badge.cache': 'Do cache',
  'badge.truncated': 'Conteúdo truncado',
  'badge.tokens': '{n} tokens',
  'badge.actions.one': '1 ação executada',
  'badge.actions.other': '{n} ações executadas',
  'badge.fetch': 'Busca: {s}s',
  'badge.parse': 'Conversão: {s}s',
  'badge.llm': 'LLM: {s}s',
  'badge.left.one': '1 extração restante',
  'badge.left.other': '{n} extrações restantes',

  'validation.passed': 'Validado pelo schema',
  'validation.failed': 'Falhou na validação do schema',
  'validation.none': 'Sem validação de schema',
  'validation.noneHint': 'Nenhum schema de saída foi definido, então nada conferiu este JSON. Adicione campos nas opções avançadas para validar.',
  'validation.missing': 'Campo obrigatório ausente: {field}',
  'validation.wrongType': "O campo '{field}' tem tipo errado. Esperado: {type}",
  'validation.notFound': "O campo obrigatório '{field}' não foi encontrado na página (null)",
  'validation.notObject': 'A saída não é um objeto JSON',

  'status.status': 'Status:',
  'status.online': 'Online',
  'status.offline': 'Fora do ar',
  'status.scrapes': 'Extrações:',
  'status.version': 'Versão:',

  'toast.starting': 'Iniciando a extração...',
  'toast.success': 'Dados extraídos com sucesso',
  'toast.fromCache': ' (do cache)',
  'toast.sample': ' (amostra pré-gravada)',

  'error.invalid_url': 'Não dá para usar essa URL. Confira se ela começa com http:// ou https:// e se o domínio existe.',
  'error.blocked_url': 'Por segurança, endereços privados, internos ou de metadados de nuvem não podem ser acessados.',
  'error.api_key_required': 'Este modelo exige sua própria chave de API. Escolha um modelo da Groq para o modo gratuito compartilhado, ou cole sua chave acima.',
  'error.provider_auth': 'O provedor recusou a chave de API. Confira a chave e tente de novo.',
  'error.provider_unavailable': 'A chave gratuita compartilhada está indisponível agora. Cole sua própria chave ou tente mais tarde.',
  'error.provider_rate_limited': 'O provedor está limitando as requisições. Aguarde um pouco ou tente outro modelo.',
  'error.provider_quota': 'A cota da API acabou. Confira os limites da sua conta.',
  'error.site_timeout': 'O site demorou demais para responder. Tente de novo.',
  'error.rate_limited': 'Muitas requisições em pouco tempo. Aguarde um momento.',
  'error.scrape_limit_reached': 'Você usou todas as extrações ao vivo desta sessão. As amostras continuam disponíveis.',
  'error.daily_limit_reached': 'A chave gratuita compartilhada atingiu o limite do dia. Cole sua própria chave de API ou volte amanhã.',
  'error.internal_error': 'Não foi possível concluir a extração.',
  'error.internal_error_ref': 'Não foi possível concluir a extração. Código de referência: {ref}',
  'error.session_expired': 'Sua sessão de demonstração expirou. Abrimos uma nova; tente de novo.',
  'error.client_timeout': 'A requisição passou de 5 minutos. Tente de novo ou use um pedido mais simples.',
  'error.network': 'Não foi possível falar com o servidor. Confira sua conexão e tente de novo.',
  'error.unknown': 'Algo deu errado. Tente de novo.',

  'session.tooMany': 'Muitas sessões de demonstração abertas a partir da sua rede nos últimos minutos. Aguarde uns dez minutos e recarregue.',
  'session.failed': 'Não foi possível abrir uma sessão de demonstração agora. Recarregue a página em instantes.',
};

const translations: Record<Locale, Dict> = { en, pt };

export type Locale = 'en' | 'pt';

export type TranslateVars = Record<string, string | number>;

export type Translate = (key: string, vars?: TranslateVars) => string;

/** Like `t`, but returns `fallback` (usually API text) when this locale has no entry. */
export type TranslateOr = (key: string, fallback: string, vars?: TranslateVars) => string;

export function isLocale(value: unknown): value is Locale {
  return value === 'en' || value === 'pt';
}

export function detectLocale(): Locale {
  if (typeof navigator === 'undefined') return 'en';
  const lang = (navigator.language || '').toLowerCase();
  if (lang.startsWith('pt')) return 'pt';
  return 'en';
}

function interpolate(template: string, vars?: TranslateVars): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in vars ? String(vars[name]) : match
  );
}

export function getTranslations(locale: Locale): Translate {
  const dict = translations[locale] || en;
  return (key, vars) => interpolate(dict[key] ?? en[key] ?? key, vars);
}

export function getTranslateOr(locale: Locale): TranslateOr {
  const dict = translations[locale] || en;
  return (key, fallback, vars) => interpolate(dict[key] ?? fallback, vars);
}
