import type { RegionFeatureCollection } from "@/models/destination.models";
import { apiConfig } from "@/shared/api/api.config";
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

    const regions: RegionFeatureCollection = await response.json();
    logger.debug("Regions data loaded", {
        regionsCount: regions.features.length,
        durationMs: Date.now() - startedAt,
    });

    return regions;
}
