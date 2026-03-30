import { useTranslation } from "react-i18next";

import { BouncingDotsLoader } from "@/components/loader/BouncingDotsLoader";
import { LoaderShell } from "@/components/loader/LoaderShell";

type TravelMapLoaderProps = {
    label?: string;
};

export function TravelMapLoader({ label }: TravelMapLoaderProps) {
    const { t } = useTranslation();
    const resolvedLabel = label ?? t("loader.loading");

    return (
        <LoaderShell label={resolvedLabel}>
            <BouncingDotsLoader />
        </LoaderShell>
    );
}
