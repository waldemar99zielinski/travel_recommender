import { useCallback } from "react";

import type { RegionFeatureCollection } from "@/models/destination/model/types";
import { fetchRegions } from "@/shared/api/regionsApi";
import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useRegionsApi(): ApiHookTuple<RegionFeatureCollection, void> {
    const request = useCallback(async () => {
        return fetchRegions();
    }, []);

    return useApiRequest<RegionFeatureCollection, void>(request);
}
