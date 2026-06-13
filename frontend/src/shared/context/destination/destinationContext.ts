import { createContext } from "react";

import type { DestinationItemDto } from "@/models/destination.models";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export interface DestinationContextValue {
    destinationsById: Record<string, DestinationItemDto>;
    destinationsStatus: FetchStatus;
    destinationsError: string | null;
    fetchDestinations: () => Promise<void>;
    getDestination: (id: string) => DestinationItemDto | undefined;
    getDestinationsByParentRegion: (parentRegionId: string) => DestinationItemDto[];
}

export const DestinationContext =
    createContext<DestinationContextValue | undefined>(undefined);
