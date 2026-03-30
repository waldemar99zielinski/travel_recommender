import { useEffect, useState } from "react";

import { CircularProgress, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { RecommendationLayout } from "@/components/recommendation/RecommendationLayout";
import { Chat } from "@/components/chat/Chat";
import type { ChatMessage } from "@/components/chat/Chat.interfaces";
import { Map } from "@/components/map/Map";
import type { RecommendationItemDto } from "@/models/recommendation/model/types";
import { useRecommendationsApi } from "@/shared/hooks/useRecommendationsApi";
import { useRegionsApi } from "@/shared/hooks/useRegionsApi";

const TEST_RECOMMENDATIONS: RecommendationItemDto[] = [
    {
        id: "DEU",
        title: "Germany",
        score: 97,
        description: "Demo recommendation for map preview.",
    },
    {
        id: "ESP_ML",
        title: "Spain, mainland",
        score: 93,
        description: "Demo recommendation for map preview.",
    },
    {
        id: "JPN",
        title: "Japan",
        score: 90,
        description: "Demo recommendation for map preview.",
    },
    {
        id: "USA_CA",
        title: "USA California",
        score: 86,
        description: "Demo recommendation for map preview.",
    },
    {
        id: "BRA_SE",
        title: "Brazil Southeast",
        score: 82,
        description: "Demo recommendation for map preview.",
    },
];

export function RecommendationPage() {
    const { t } = useTranslation();
    const [regions, regionsStatus, regionsError, fetchRegionsData] =
        useRegionsApi();
    const [
        recommendationResponse,
        recommendationsStatus,
        recommendationsError,
        fetchRecommendationsData,
    ] = useRecommendationsApi();
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [selectedRegionId, setSelectedRegionId] = useState<string | null>(
        TEST_RECOMMENDATIONS[0].id,
    );

    const recommendations: RecommendationItemDto[] =
        recommendationResponse?.recommendations ?? TEST_RECOMMENDATIONS;
    useEffect(() => {
        void fetchRegionsData();
    }, [fetchRegionsData]);

    const handleSubmit = async () => {
        const userMessage = message.trim();
        if (userMessage.length === 0) {
            return;
        }

        setMessages((previous) => [
            ...previous,
            {
                id: `user-${Date.now()}`,
                role: "user",
                content: userMessage,
            },
        ]);
        setMessage("");

        const response = await fetchRecommendationsData({
            user_id: "user_1",
            session_id: "session_1",
            message: userMessage,
        });

        if (response != null) {
            setMessages((previous) => [
                ...previous,
                {
                    id: `assistant-${Date.now()}`,
                    role: "assistant",
                    content: response.message,
                    onClick:
                        response.recommendations.length > 0
                            ? () => {
                                  setSelectedRegionId(
                                      response.recommendations[0].id,
                                  );
                              }
                            : undefined,
                },
            ]);
            setSelectedRegionId(response.recommendations[0]?.id ?? null);
        }
    };

    const isLoadingRegions = regionsStatus === "loading";
    const isLoadingRecommendations = recommendationsStatus === "loading";
    const errorMessage = regionsError ?? recommendationsError;

    if (isLoadingRegions || regions == null) {
        return (
            <Stack
                sx={{ height: "100%" }}
                alignItems="center"
                justifyContent="center"
                spacing={2}
            >
                <CircularProgress />
                <Typography color="text.secondary">
                    {t("recommendation.loadingMapData")}
                </Typography>
            </Stack>
        );
    }

    return (
        <RecommendationLayout
            chat={
                <Chat
                    messages={messages}
                    message={message}
                    onMessageChange={setMessage}
                    onSubmit={handleSubmit}
                    isLoading={isLoadingRecommendations}
                    errorMessage={errorMessage}
                />
            }
            map={
                <Map
                    regions={regions}
                    recommendations={recommendations}
                    selectedRegionId={selectedRegionId}
                    onSelectRegion={setSelectedRegionId}
                />
            }
        />
    );
}
