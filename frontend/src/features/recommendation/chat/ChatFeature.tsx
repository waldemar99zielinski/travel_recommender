import { useState } from "react";

import { Chat } from "@/components/chat/Chat";
import { NewSessionButton } from "@/features/recommendation/chat/components/NewSessionButton";
import { useRecommendationFeatureContext } from "@/features/recommendation/useRecommendationFeatureContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "ChatFeature" });

export function ChatFeature() {
    const [message, setMessage] = useState("");
    const {
        messages,
        startNewSession,
        submitRecommendationMessage,
        isLoading,
        errorMessage,
    } = useRecommendationFeatureContext();

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
                messages={messages}
                message={message}
                onMessageChange={setMessage}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                errorMessage={errorMessage}
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
