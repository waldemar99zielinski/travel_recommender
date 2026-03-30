import "i18next";

import type { translationEn } from "@/app/providers/i18n/resources/en";

declare module "i18next" {
    interface CustomTypeOptions {
        defaultNS: "translation";
        resources: {
            translation: typeof translationEn;
        };
    }
}
