import type { Translate } from "@/lib/i18n";

/** A failure the UI shows: a code to translate and the API text as fallback. */
export interface UiError {
  code: string;
  message: string;
}

/**
 * Message for the visitor in the current language. The API speaks English and
 * sends a stable `error_code`; the code picks the translation and the API text
 * is only used when the code is unknown (a newer backend than this frontend).
 */
export function describeError(error: UiError, t: Translate): string {
  const { code, message } = error;

  if (code === "internal_error") {
    const ref = /Reference ID:\s*([A-Za-z0-9]+)/.exec(message)?.[1];
    return ref ? t("error.internal_error_ref", { ref }) : t("error.internal_error");
  }

  const key = `error.${code}`;
  const translated = t(key);
  if (translated !== key) return translated;

  return message || t("error.unknown");
}

/** Translate the validator's English lines; unknown lines pass through. */
export function describeValidationError(line: string, t: Translate): string {
  let m = /^Missing required field: (.+)$/.exec(line);
  if (m) return t("validation.missing", { field: m[1] });

  m = /^Field '(.+)' has wrong type\. Expected (.+)$/.exec(line);
  if (m) return t("validation.wrongType", { field: m[1], type: m[2] });

  m = /^Required field '(.+)' was not found on the page \(null\)$/.exec(line);
  if (m) return t("validation.notFound", { field: m[1] });

  if (line === "Output is not a JSON object") return t("validation.notObject");

  return line;
}
