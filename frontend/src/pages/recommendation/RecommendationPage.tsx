import { useEffect } from "react";
import {
    Alert,
    CircularProgress,
    Stack,
    Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

import { RecommendationLayout } from "@/components/recommendation/RecommendationLayout";
import {
    ChatFeature,
    MapFeature,
    RecommendationFeatureProvider,
} from "@/features/recommendation";
import { useRegionsApi } from "@/shared/hooks/useRegionsApi";
import { createLogger } from "@/shared/lib/logger";

const logger = createLogger({ scope: "RecommendationPage" });

export function RecommendationPage() {
    const { t } = useTranslation();
    const [regions, regionsStatus, regionsError, fetchRegionsData] = useRegionsApi();

     useEffect(() => {
        const loadRegions = async () => {
            logger.trace("Fetching regions for map");

            const result = await fetchRegionsData();
            if (result == null) {
                logger.warn("Map regions request finished without data");
                return;
            }

            logger.debug("Map regions ready", {
                regionsCount: result.features.length,
            });
        };

        void loadRegions();
    }, [fetchRegionsData]);

     if (regionsStatus === "loading") {
        return (
            <Stack
                sx={{ height: "100%", alignItems: "center", justifyContent: "center" }}
                spacing={2}
            >
                <CircularProgress />
                <Typography color="text.secondary">
                    {t("recommendation.loadingMapData")}
                </Typography>
            </Stack>
        );
    }

    if (regionsError != null) {
        logger.error("Error loading regions for map", {
            error: regionsError,
        });

        return (
            <Stack sx={{ height: "100%", p: 2, justifyContent: "center" }}>
                <Alert severity="error">{regionsError}</Alert>
            </Stack>
        );
    }

    if (regions == null) {
        return (
            <Stack sx={{ height: "100%", p: 2, justifyContent: "center" }}>
                <Alert severity="error">
                    {t("recommendation.noRegionsFound")}
                </Alert>
            </Stack>
        );
    }

    return (
        <RecommendationFeatureProvider regions={regions}>
            <RecommendationLayout chat={<ChatFeature />} map={<MapFeature />} />
        </RecommendationFeatureProvider>
    );
}
