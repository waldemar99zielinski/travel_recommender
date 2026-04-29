import {
    type SessionCreateRequestDto,
    type SessionCreateResponseDto,
    type SessionDeleteResponseDto,
    type SessionRefDto,
    type SessionStateResponseDto,
    validateSessionCreateRequestDto,
    validateSessionCreateResponseDto,
    validateSessionDeleteResponseDto,
    validateSessionRefDto,
    validateSessionStateResponseDto,
} from "@/models/session.models";
import { sessionApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "SessionApi" });

export async function createSession(
    payload: SessionCreateRequestDto = {},
): Promise<SessionCreateResponseDto> {
    const requestPayload = validateSessionCreateRequestDto(payload);
    const startedAt = Date.now();
    const url = sessionApiUrlBuilder.createSession();
    const userId = requestPayload.user_id?.trim();
    const bodyPayload: SessionCreateRequestDto | undefined =
        userId == null || userId.length === 0 ? undefined : { user_id: userId };

    logger.trace("Creating session", {
        url,
        userId,
    });

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: bodyPayload == null ? undefined : JSON.stringify(bodyPayload),
    });

    if (!response.ok) {
        logger.error("Create session request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(`Create session request failed with status ${response.status}`);
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateSessionCreateResponseDto(rawResponseData);

    logger.debug("Session created", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        responseData,
    });

    return responseData;
}

export async function getSession(
    session: SessionRefDto,
): Promise<SessionStateResponseDto> {
    const validSession = validateSessionRefDto(session);
    const startedAt = Date.now();
    const url = sessionApiUrlBuilder.getSession(
        validSession.user_id,
        validSession.session_id,
    );

    logger.trace("Loading session", {
        url,
        session: validSession,
    });

    const response = await fetch(url);

    if (!response.ok) {
        logger.error("Get session request failed", {
            status: response.status,
            statusText: response.statusText,
            session: validSession,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(`Get session request failed with status ${response.status}`);
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateSessionStateResponseDto(rawResponseData);

    logger.debug("Session loaded", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        session: validSession,
        responseData,
    });

    return responseData;
}

export async function removeSession(
    session: SessionRefDto,
): Promise<SessionDeleteResponseDto> {
    const validSession = validateSessionRefDto(session);
    const startedAt = Date.now();
    const url = sessionApiUrlBuilder.removeSession(
        validSession.user_id,
        validSession.session_id,
    );

    logger.trace("Removing session", {
        url,
        session: validSession,
    });

    const response = await fetch(url, {
        method: "DELETE",
    });

    if (!response.ok) {
        logger.error("Delete session request failed", {
            status: response.status,
            statusText: response.statusText,
            session: validSession,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(`Delete session request failed with status ${response.status}`);
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateSessionDeleteResponseDto(rawResponseData);

    logger.debug("Session removed", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        session: validSession,
        responseData,
    });

    return responseData;
}
