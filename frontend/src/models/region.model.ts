import type { FeatureCollection, Geometry } from "geojson";
import { z } from "zod";

import type { RecommendationItemDto } from "@/models/recommendation.models";

export interface RegionFeatureProperties {
    u_name: string;
    display_name: string;
}

export interface RegionFeatureDto {
    type: "Feature";
    properties: RegionFeatureProperties;
    geometry: unknown | null;
}

export interface RegionFeatureCollectionDto {
    type: "FeatureCollection";
    features: RegionFeatureDto[];
}

export const regionFeaturePropertiesSchema = z.looseObject({
    u_name: z.string().trim().min(1),
    display_name: z.string().trim().min(1),
}) satisfies z.ZodType<RegionFeatureProperties>;

export const regionFeatureDtoSchema = z.looseObject({
    type: z.literal("Feature"),
    properties: regionFeaturePropertiesSchema,
    geometry: z.unknown().nullable(),
}) satisfies z.ZodType<RegionFeatureDto>;

export const regionFeatureCollectionDtoSchema = z.looseObject({
    type: z.literal("FeatureCollection"),
    features: z.array(regionFeatureDtoSchema),
}) satisfies z.ZodType<RegionFeatureCollectionDto>;

export interface RegionFeatureCollection extends FeatureCollection<
    Geometry,
    RegionFeatureProperties
> {}

export interface EnrichedRegionFeatureProperties extends RegionFeatureProperties {
    recommendation?: RecommendationItemDto;
    rank?: number;
}

export interface EnrichedRegionFeatureCollection extends FeatureCollection<
    Geometry,
    EnrichedRegionFeatureProperties
> {}

export function validateRegionFeatureCollectionDto(
    payload: unknown,
): RegionFeatureCollection {
    return regionFeatureCollectionDtoSchema.parse(payload) as RegionFeatureCollection;
}
