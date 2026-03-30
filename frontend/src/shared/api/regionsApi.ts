import type { RegionFeatureCollection } from "@/models/destination/model/types";

export async function fetchRegions(): Promise<RegionFeatureCollection> {
    const response = await fetch("/regions.json");
    if (!response.ok) {
        throw new Error(
            `Regions data request failed with status ${response.status}`,
        );
    }

    const regions: RegionFeatureCollection = await response.json();

    return regions;
}
