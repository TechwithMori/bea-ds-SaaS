import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fa, en, words, type MessageKey } from "./messages";

export type Lang = "fa" | "en";

const STORAGE_KEY = "bea.lang";
const dictionaries = { fa, en };

type LanguageValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: MessageKey, vars?: Record<string, string | number>) => string;
  word: (value: string) => string;
};

const LanguageContext = createContext<LanguageValue | null>(null);

function readLang(): Lang {
  return localStorage.getItem(STORAGE_KEY) === "en" ? "en" : "fa";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readLang);

  useEffect(() => {
    document.documentElement.lang = lang === "fa" ? "fa" : "en";
    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
    localStorage.setItem(STORAGE_KEY, lang);
  }, [lang]);

  const value = useMemo<LanguageValue>(() => {
    return {
      lang,
      setLang(next) {
        setLangState(next);
      },
      t(key, vars) {
        let text: string = dictionaries[lang][key];
        if (vars) {
          for (const [name, replacement] of Object.entries(vars)) {
            text = text.replaceAll(`{${name}}`, String(replacement));
          }
        }
        return text;
      },
      word(value) {
        const table = words[lang] as Record<string, string>;
        return table[value] ?? value;
      },
    };
  }, [lang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useI18n() {
  const value = useContext(LanguageContext);
  if (!value) throw new Error("useI18n must be used inside LanguageProvider");
  return value;
}

export function LanguageSwitch() {
  const { lang, setLang, t } = useI18n();
  return (
    <div className="flex rounded-full border border-line p-0.5 text-sm">
      <button
        type="button"
        className={`rounded-full px-2.5 py-1 ${lang === "fa" ? "bg-ink text-cream" : ""}`}
        onClick={() => setLang("fa")}
      >
        {t("langFa")}
      </button>
      <button
        type="button"
        className={`rounded-full px-2.5 py-1 ${lang === "en" ? "bg-ink text-cream" : ""}`}
        onClick={() => setLang("en")}
      >
        {t("langEn")}
      </button>
    </div>
  );
}
