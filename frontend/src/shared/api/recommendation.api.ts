import type { RecommendationRequestDto } from "@/models/recommendation.models";
import type { RecommendationStreamEvent } from "@/models/recommendation.stream.models";
import { apiConfig } from "@/shared/api/config.api";
import { streamSse } from "@/shared/api/sseStream";
import { createRecommendationApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RecommendationApi" });

export async function* streamRecommendations(
    payload: RecommendationRequestDto,
): AsyncGenerator<RecommendationStreamEvent> {
    const url = createRecommendationApiUrlBuilder(
        apiConfig.baseUrl,
        payload.session.version, 
    ).fetchRecommendations();

    logger.trace("Starting recommendation SSE stream", {
        url,
        payload,
    });

    const sseStream = streamSse(url, payload);

    for await (const sseEvent of sseStream) {
        logger.trace("SSE event received", {
            event: sseEvent.event,
            data: sseEvent.data,
        });

        yield sseEvent;
    }
}
