'use client';

import { createContext, useContext, useEffect, useMemo, type ReactNode } from 'react';
import { useLocale } from '@/hooks/use-locale';
import {
  getTranslateOr,
  getTranslations,
  type Locale,
  type Translate,
  type TranslateOr,
} from '@/lib/i18n';

interface I18nValue {
  locale: Locale;
  t: Translate;
  tOr: TranslateOr;
  changeLocale: (locale: Locale) => void;
}

// One locale for the whole page. Before, the landing copy called useLocale on
// its own and the scraper widget never received the choice, which is why the
// form stayed in English with PT selected.
const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const { locale, changeLocale } = useLocale();

  const value = useMemo<I18nValue>(
    () => ({
      locale,
      t: getTranslations(locale),
      tOr: getTranslateOr(locale),
      changeLocale,
    }),
    [locale, changeLocale]
  );

  // Screen readers and the browser's translate prompt read <html lang>.
  useEffect(() => {
    document.documentElement.lang = locale === 'pt' ? 'pt-BR' : 'en';
  }, [locale]);

  // React 19 hoists <title> into <head>; it is prerendered in English (server
  // snapshot) and follows the chosen language on the client.
  return (
    <I18nContext.Provider value={value}>
      <title>{value.t('meta.title')}</title>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useI18n must be used inside <I18nProvider>');
  }
  return ctx;
}
