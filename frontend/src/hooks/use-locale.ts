'use client';
import { useCallback, useSyncExternalStore } from 'react';
import { type Locale, detectLocale, isLocale } from '@/lib/i18n';

const LOCALE_KEY = 'preferred-locale';

// The chosen locale is external state (localStorage + navigator), so it is read
// through useSyncExternalStore instead of copied into React state inside an
// effect. The server snapshot is 'en' (the page is prerendered); the client
// switches right after hydration without a mismatch warning.
const listeners = new Set<() => void>();

// Keeps the choice working even when storage is blocked (private mode, denied
// site data): the toggle must still switch the language for this page view.
let memoryLocale: Locale | null = null;

function readStoredLocale(): Locale | null {
  try {
    const stored = window.localStorage.getItem(LOCALE_KEY);
    return isLocale(stored) ? stored : null;
  } catch {
    return null;
  }
}

function getSnapshot(): Locale {
  return memoryLocale ?? readStoredLocale() ?? detectLocale();
}

function getServerSnapshot(): Locale {
  return 'en';
}

function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  window.addEventListener('storage', onChange);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener('storage', onChange);
  };
}

export function useLocale() {
  const locale = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const changeLocale = useCallback((newLocale: Locale) => {
    memoryLocale = newLocale;
    try {
      window.localStorage.setItem(LOCALE_KEY, newLocale);
    } catch {
      // Storage unavailable: the in-memory choice still applies.
    }
    listeners.forEach((notify) => notify());
  }, []);

  return { locale, changeLocale };
}
