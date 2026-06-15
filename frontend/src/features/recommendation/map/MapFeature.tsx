import { useCallback } from "react";

import {
    Box,
} from "@mui/material";

import { Map } from "@/components/map/Map";
import { OverlayPanelFeature } from "@/features/recommendation/map/OverlayPanelFeature";
import { useRecommendationFeatureContext } from "@/features/recommendation/context/useRecommendationFeatureContext";
import {
    getLatestTurnWithRecommendations,
    hasRecommendations,
} from "@/models/chat.models";
import { recommendationItemDtoSchema } from "@/models/recommendation.models";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "MapFeature" });

export function MapFeature() {
    // const { t } = useTranslation();
    const {
        regions,

        chatState: { chatRecords, onGoingChatTurn },
        mapState: {
            selectedRegionId,
            setSelectedRegionId,
            focusedRegionId,
            setFocusedRegionId,
            regionForRecommendationSelection: {
                selectionMode,
                setSelectionMode,
                regionSelectedForRecommendationStatus,
                setRegionSelectedForRecommendationStatus,
                addRegionsToDraftSelection,
                moveDraftSelectionToIncluded,
                moveDraftSelectionToExcluded,
                clearDraftSelectedRegionIds,
            },
        },
    } = useRecommendationFeatureContext();

    const currentAssistantTurn = onGoingChatTurn ?? chatRecords.at(-1) ?? null;
    const recommendationSourceTurn = hasRecommendations(currentAssistantTurn)
        ? currentAssistantTurn
        : getLatestTurnWithRecommendations(chatRecords);
    const parsedRecommendations = recommendationItemDtoSchema
        .array()
        .safeParse(recommendationSourceTurn?.recommendations ?? []);
    const latestRecommendations = parsedRecommendations.success
        ? parsedRecommendations.data
        : [];

    const handleRegionSelect = useCallback(
        (regionId: string | null) => {
            setSelectedRegionId(regionId);
            setFocusedRegionId(null);
            logger.trace("Region selected on map", { regionId });
        },
        [setSelectedRegionId, setFocusedRegionId],
    );


    return (
        <Box
            sx={{
                position: "relative",
                display: "flex",
                flex: 1,
                minHeight: { xs: 420, lg: "100%" },
            }}
        >
            <Map
                regions={regions}
                recommendations={latestRecommendations}
                selectedRegionId={selectedRegionId}
                focusedRegionId={focusedRegionId}
                onSelectRegion={handleRegionSelect}
                selectionForRecommendationProps={{
                    selectionMode,
                    setSelectionMode,
                    regionSelectedForRecommendationStatus,
                    addRegionsToDraftSelection,
                    setRegionSelectedForRecommendationStatus,
                    moveDraftSelectionToIncluded,
                    moveDraftSelectionToExcluded,
                    clearDraftSelectedRegionIds,
                }}
            />

            <OverlayPanelFeature />
        </Box>
    );
}
