import { useCallback, useMemo } from "react";

import type { DestinationItemDto } from "@/models/destination.models";
import { fetchDestinations as fetchDestinationsRequest } from "@/shared/api/destinations.api";
import type { DestinationContextValue } from "@/shared/context/destination/destinationContext";
import { useApiRequest } from "@/shared/hooks/useApiRequest";
import type { DestinationListResponseDto } from "@/models/destination.models";

export function useDestinationContextValue(): DestinationContextValue {
    const [destinationsData, destinationsStatus, destinationsError, triggerFetch] =
        useApiRequest<DestinationListResponseDto>(fetchDestinationsRequest, {
            requestName: "destinations",
        });

    const destinationsById = useMemo<Record<string, DestinationItemDto>>(() => {
        if (destinationsData == null) {
            return {};
        }

        return destinationsData.destinations.reduce<
            Record<string, DestinationItemDto>
        >((acc, destination) => {
            acc[destination.id] = destination;
            return acc;
        }, {});
    }, [destinationsData]);

    const destinationByParentRegion = useMemo<Record<string, DestinationItemDto[]>>(() => {
        if (destinationsData == null) {
            return {};
        }

        return destinationsData.destinations.reduce<
            Record<string, DestinationItemDto[]>
        >((acc, destination) => {
            const parentRegion = destination.parent_region;
            if (!acc[parentRegion]) {
                acc[parentRegion] = [];
            }
            acc[parentRegion].push(destination);
            return acc;
        }, {});
    }, [destinationsData]);

    const getDestination = useCallback(
        (id: string): DestinationItemDto | undefined => {
            return destinationsById[id];
        },
        [destinationsById],
    );

    const getDestinationsByParentRegion = useCallback(
        (parentRegionId: string): DestinationItemDto[] => {
            return destinationByParentRegion[parentRegionId] || [];
        },
        [destinationByParentRegion],
    );

    const fetchDestinations = useCallback(async (): Promise<void> => {
        await triggerFetch();
    }, [triggerFetch]);

    return {
        destinationsById,
        destinationsStatus,
        destinationsError,
        fetchDestinations,
        getDestination,
        getDestinationsByParentRegion,
    };
}
