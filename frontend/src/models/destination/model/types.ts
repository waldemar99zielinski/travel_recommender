import type { FeatureCollection, Geometry } from "geojson";

import type { RecommendationItemDto } from "@/models/recommendation/model/types";

export type RegionFeatureProperties = {
    u_name: string;
    display_name?: string;
    name?: string;
    country?: string;
};

export type RegionFeatureCollection = FeatureCollection<
    Geometry,
    RegionFeatureProperties
>;

export type EnrichedRegionFeatureProperties = RegionFeatureProperties & {
    recommendation?: RecommendationItemDto;
    rank?: number;
};

export type EnrichedRegionFeatureCollection = FeatureCollection<
    Geometry,
    EnrichedRegionFeatureProperties
>;
