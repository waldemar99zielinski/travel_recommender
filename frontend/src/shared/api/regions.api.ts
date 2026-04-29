import {
    type RegionFeatureCollection,
    validateRegionFeatureCollectionDto,
} from "@/models/region.model";
import { apiConfig } from "@/shared/api/config.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RegionsApi" });

export async function fetchRegions(): Promise<RegionFeatureCollection> {
    const startedAt = Date.now();
    logger.trace("Requesting regions data", {
        url: apiConfig.regionsDataUrl,
    });

    const response = await fetch(apiConfig.regionsDataUrl);
    if (!response.ok) {
        logger.error("Regions data request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Regions data request failed with status ${response.status}`,
        );
    }

    const rawData: unknown = await response.json();
    const regions = validateRegionFeatureCollectionDto(rawData);
    logger.debug("Regions data loaded", {
        regionsCount: regions.features.length,
        durationMs: Date.now() - startedAt,
    });

    return regions;
}
