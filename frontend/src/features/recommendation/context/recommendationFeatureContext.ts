import { createContext } from "react";

import type { RecommendationItemDto } from "@/models/recommendation.models";
import type { UseRecommendationMapStateReturn } from "@/features/recommendation/context/handlers/useRecommendationMapState";
import type { RegionFeatureCollection } from "@/models/region.model";
import type { UseRecommendationSessionReturn } from "@/features/recommendation/context/handlers/useRecommendationSession";
import type { UseRecommendationChat } from "@/features/recommendation/context/handlers/useRecommendationChat";

export type OverlayPanelType = "region-detail" | "destination-detail";

export interface RegionDetailOverlayPanelData {
    id: string;
    name?: string;
    recommendation?: RecommendationItemDto;
}

export interface DestinationDetailOverlayPanelData {
    id: string;
    name?: string;
}

export type OverlayPanelState =
    | {
        title: string;
        type: "region-detail";
        data: RegionDetailOverlayPanelData;
    }
    | {
        title: string;
        type: "destination-detail";
        data: DestinationDetailOverlayPanelData;
    };

export interface RecommendationFeatureContextValue {
    regions: RegionFeatureCollection;
    mapState: UseRecommendationMapStateReturn;
    sessionState: UseRecommendationSessionReturn;
    chatState: UseRecommendationChat;
    overlayPanel: OverlayPanelState | null;
}

export const RecommendationFeatureContext =
    createContext<RecommendationFeatureContextValue | undefined>(undefined);
