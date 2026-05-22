import { useEffect } from "react";

import { Alert, CircularProgress, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { Map } from "@/components/map/Map";
import { useRecommendationFeatureContext } from "@/features/recommendation/useRecommendationFeatureContext";
import { useRegionsApi } from "@/shared/hooks/useRegionsApi";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "MapFeature" });

export function MapFeature() {
    const { t } = useTranslation();
    const [regions, regionsStatus, regionsError, fetchRegionsData] = useRegionsApi();
    const {
        recommendationResponse,
        selectedRegionId,
        setSelectedRegionId,
        focusedRegionId,
        setFocusedRegionId,
    } = useRecommendationFeatureContext();

    const recommendations = recommendationResponse?.recommendations ?? [];

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

    useEffect(() => {
        if (regionsError == null) {
            return;
        }

        logger.error("Unable to load map regions", {
            error: regionsError,
        });
    }, [regionsError]);

    if (regionsStatus === "loading") {
        return (
            <Stack
                sx={{ height: "100%" }}
                alignItems="center"
                justifyContent="center"
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
        return (
            <Stack sx={{ height: "100%", p: 2 }} justifyContent="center">
                <Alert severity="error">{regionsError}</Alert>
            </Stack>
        );
    }

    if (regions == null) {
        return (
            <Stack sx={{ height: "100%", p: 2 }} justifyContent="center">
                <Alert severity="error">
                    {t("recommendation.noRegionsFound")}
                </Alert>
            </Stack>
        );
    }

    return (
        <Map
            regions={regions}
            recommendations={recommendations}
            selectedRegionId={selectedRegionId}
            focusedRegionId={focusedRegionId}
            rankingConfig={{
                topN: 10,
                labelMode: "rank",
            }}
            onSelectRegion={(regionId) => {
                setSelectedRegionId(regionId);
                setFocusedRegionId(null);
                logger.trace("Region selected on map", { regionId });
            }}
        />
    );
}
