import { useCallback } from "react";

import type { RegionFeatureCollection } from "@/models/region.model";
import { fetchRegions } from "@/shared/api/regions.api";
import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useRegionsApi(): ApiHookTuple<RegionFeatureCollection, void> {
    const request = useCallback(async () => {
        return fetchRegions();
    }, []);

    return useApiRequest<RegionFeatureCollection, void>(request, {
        requestName: "regions",
    });
}
