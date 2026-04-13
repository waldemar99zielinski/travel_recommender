import type { RegionFeatureCollection } from "@/models/destination.models";
import { apiConfig } from "@/shared/api/api.config";

export async function fetchRegions(): Promise<RegionFeatureCollection> {
    const response = await fetch(apiConfig.regionsDataUrl);
    if (!response.ok) {
        throw new Error(
            `Regions data request failed with status ${response.status}`,
        );
    }

    const regions: RegionFeatureCollection = await response.json();

    return regions;
}
