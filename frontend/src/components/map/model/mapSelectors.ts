import type {
    EnrichedRegionFeatureCollection,
    EnrichedRegionFeatureProperties,
    RegionFeatureCollection,
} from "@/models/destination/model/types";
import type { RecommendationItemDto } from "@/models/recommendation/model/types";

export function enrichRegions(
    regions: RegionFeatureCollection,
    recommendations: RecommendationItemDto[],
): EnrichedRegionFeatureCollection {
    const recommendationsByScore = [...recommendations].sort((left, right) => {
        if (right.score !== left.score) {
            return right.score - left.score;
        }

        return left.id.localeCompare(right.id);
    });

    const rankedById = new Map(
        recommendationsByScore.map((recommendation, index) => [
            recommendation.id,
            { recommendation, rank: index + 1 },
        ]),
    );

    return {
        ...regions,
        features: regions.features.map((feature) => {
            const ranked = rankedById.get(feature.properties.u_name);
            const properties: EnrichedRegionFeatureProperties = {
                ...feature.properties,
                recommendation: ranked?.recommendation,
                rank: ranked?.rank,
            };

            return {
                ...feature,
                properties,
            };
        }),
    };
}
