export type RecommendationItemDto = {
    id: string;
    title: string;
    score: number;
    description: string;
};

export type RecommendationResponseDto = {
    message: string;
    recommendations: RecommendationItemDto[];
};

export type RecommendationRequestDto = {
    user_id: string;
    session_id: string;
    message: string;
};
