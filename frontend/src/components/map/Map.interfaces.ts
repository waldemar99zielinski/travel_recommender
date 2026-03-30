import type {
    EnrichedRegionFeatureCollection,
    EnrichedRegionFeatureProperties,
    RegionFeatureCollection,
} from "@/models/destination/model/types";
import type { RecommendationItemDto } from "@/models/recommendation/model/types";

export type MapRankingLabelMode = "rank" | "score" | "rank-score";

export interface MapRegionRankingConfig {
    topN?: number;
    labelMode?: MapRankingLabelMode;
    forceTopColor?: boolean;
}

export interface MapProps {
    regions: RegionFeatureCollection;
    recommendations: RecommendationItemDto[];
    selectedRegionId: string | null;
    onSelectRegion: (regionId: string | null) => void;
    rankingConfig?: MapRegionRankingConfig;
}

export interface MapCanvasProps {
    enrichedRegions: EnrichedRegionFeatureCollection;
    selectedRegionId: string | null;
    onSelectRegion: (regionId: string | null) => void;
    rankingConfig: Required<MapRegionRankingConfig>;
}

export interface MapPopupCardProps {
    properties: EnrichedRegionFeatureProperties;
}

export interface MapRankLabelProps {
    rank: number;
    score: number;
    mode: MapRankingLabelMode;
}
