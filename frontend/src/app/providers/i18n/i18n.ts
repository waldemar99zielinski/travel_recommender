import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import { translationEn } from "@/app/providers/i18n/resources/en";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "i18n" });

void i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources: {
            en: {
                translation: translationEn,
            },
        },
        supportedLngs: ["en"],
        fallbackLng: "en",
        defaultNS: "translation",
        ns: ["translation"],
        load: "languageOnly",
        interpolation: {
            escapeValue: false,
        },
        returnNull: false,
        detection: {
            order: ["querystring", "localStorage", "navigator"],
            caches: ["localStorage"],
        },
    })
    .then(() => {
        logger.debug("i18n initialized", {
            language: i18n.language,
        });
    })
    .catch((error) => {
        logger.error("i18n initialization failed", error);
    });

export { i18n };
