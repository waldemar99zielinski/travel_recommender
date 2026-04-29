import {
    type HealthResponseDto,
    validateHealthResponseDto,
} from "@/models/health.models";
import { healthApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "HealthApi" });

export async function fetchHealth(): Promise<HealthResponseDto> {
    const startedAt = Date.now();
    const url = healthApiUrlBuilder.fetchHealth();

    logger.trace("Sending health check request", {
        url,
    });

    const response = await fetch(url);
    if (response.status !== 200 && response.status !== 503) {
        logger.error("Health check request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Health check request failed with unexpected status ${response.status}`,
        );
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateHealthResponseDto(rawResponseData);

    logger.debug("Health check request completed", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        responseData,
    });

    return responseData;
}
