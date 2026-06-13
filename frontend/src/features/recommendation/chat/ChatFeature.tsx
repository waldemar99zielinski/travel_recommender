import { useCallback, useState } from "react";

import { Chat } from "@/components/chat/Chat";
import { normalizeRegionId } from "@/components/map/model/mapSelectors";
import { STEP_LABELS } from "@/features/recommendation/context/handlers/useRecommendationChat";
import { NewSessionButton } from "@/features/recommendation/chat/components/NewSessionButton";
import { useRecommendationFeatureContext } from "@/features/recommendation/context/useRecommendationFeatureContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "ChatFeature" });

export function ChatFeature() {
    const [message, setMessage] = useState("");
    const {
        regions,
        chatState: {
            chatRecords,
            onGoingChatTurn,
            step,
            destinationResearchStarted,
            submitRecommendationMessage,
        },
        mapState: { setSelectedRegionId, setFocusedRegionId },
        sessionState: {
            startNewSession,
            createSessionStatus,
            createSessionError,
            getSessionStatus,
            getSessionError,
        },
    } = useRecommendationFeatureContext();

    const handleRecommendationSelect = useCallback(
        (regionId: string) => {
            const resolvedRegionId =
                regions.features.find(
                    (feature) =>
                        normalizeRegionId(feature.properties.u_name) ===
                        normalizeRegionId(regionId),
                )?.properties.u_name ?? regionId;

            setSelectedRegionId(resolvedRegionId);
            setFocusedRegionId(resolvedRegionId);
        },
        [regions, setFocusedRegionId, setSelectedRegionId],
    );

    const isLoading =
        (step !== "idle" && step !== "done" && step !== "error") ||
        createSessionStatus === "loading" ||
        getSessionStatus === "loading";

    const loadingDetail =
        isLoading && step !== "recommendation" && step !== "response"
            ? (STEP_LABELS[step] ?? null)
            : null;

    const errorMessage = createSessionError ?? getSessionError;
    const isDestinationResearchLoading =
        onGoingChatTurn != null && destinationResearchStarted;

    const handleSubmit = async () => {
        const userMessage = message.trim();
        if (userMessage.length === 0) {
            logger.debug("Ignored empty message submit");
            return;
        }

        try {
            setMessage("");
            await submitRecommendationMessage(userMessage);
        } catch (error) {
            logger.error("Failed to submit chat message", error);
        }
    };

    const handleConfirmNewSession = async () => {
        try {
            await startNewSession();
            setMessage("");
        } catch (error) {
            logger.error("Failed to start new session", error);
        }
    };

    return (
        <>
            <Chat
                chatRecords={chatRecords}
                onGoingChatTurn={onGoingChatTurn}
                message={message}
                onMessageChange={setMessage}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                loadingDetail={loadingDetail}
                loadingStep={loadingDetail != null ? step : null}
                isDestinationResearchLoading={isDestinationResearchLoading}
                errorMessage={errorMessage}
                onRecommendationSelect={handleRecommendationSelect}
                headerAction={
                    <NewSessionButton
                        disabled={isLoading}
                        onConfirm={handleConfirmNewSession}
                    />
                }
            />
        </>
    );
}
