import { RecommendationLayout } from "@/components/recommendation/RecommendationLayout";
import {
    ChatFeature,
    MapFeature,
    RecommendationFeatureProvider,
} from "@/features/recommendation";

export function RecommendationPage() {
    return (
        <RecommendationFeatureProvider>
            <RecommendationLayout chat={<ChatFeature />} map={<MapFeature />} />
        </RecommendationFeatureProvider>
    );
}
