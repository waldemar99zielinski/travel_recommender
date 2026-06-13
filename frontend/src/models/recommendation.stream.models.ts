import type { RecommendationV2RegionResearchDto } from "@/models/recommendation.models";

export interface TravelDestinationRegionFilter {
    field_name: "parent_region" | "region";
    region_name: string;
    type: "include" | "exclude";
}

export interface TravelDestinationSeasonalityFilter {
    season?: string;
    months?: string[];
}

export interface TravelDestinationBudgetCostTerm {
    explicit?: {
        value: number;
        operator: "max" | "min" | "around";
        duration: "day" | "week" | "month";
    };
    inferred_level?: "low" | "medium" | "high";
}

export interface TravelDestinationBudgetFilter {
    min_cost_per_week?: number;
    cost_term?: TravelDestinationBudgetCostTerm;
    max_cost_per_week?: number;
}

export interface TravelDestinationFilter {
    parent_region_filters?: TravelDestinationRegionFilter[];
    direct_region_filters?: TravelDestinationRegionFilter[];
    seasonality?: TravelDestinationSeasonalityFilter;
    budget?: TravelDestinationBudgetFilter;
}

export type ProgressStage =
    | "idle"
    | "initializing"
    | "validating_request"
    | "gathering_filter"
    | "recommendation_generation"
    | "recommendation"
    | "desination_research_generation"
    | "destination_research"
    | "response_generation"
    | "response"
    | "done"
    | "error";

export interface RecommendationDestinationResearchGenerationEventData {
    region_id: string;
}

export interface RecommendationDestinationResearchEventData {
    region_id: string;
    destination_research: RecommendationV2RegionResearchDto;
}

export interface RecommendationStreamEvent {
    event: string;
    data: unknown;
}
