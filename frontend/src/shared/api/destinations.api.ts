import type { DestinationListResponseDto } from "@/models/destination.models";
import { validateDestinationListResponseDto } from "@/models/destination.models";
import { destinationApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "DestinationsApi" });

export async function fetchDestinations(): Promise<DestinationListResponseDto> {
    const startedAt = Date.now();
    const url = destinationApiUrlBuilder.listDestinations();

    logger.trace("Fetching destinations", {
        url,
    });

    const response = await fetch(url);
    if (!response.ok) {
        logger.error("Destinations request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Destinations request failed with status ${response.status}`,
        );
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateDestinationListResponseDto(rawResponseData);

    logger.debug("Destinations fetched", {
        total: responseData.total,
        durationMs: Date.now() - startedAt,
    });

    return responseData;
}
