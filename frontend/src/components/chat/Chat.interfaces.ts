import type { ReactNode } from "react";

import type { ChatRecordDto } from "@/models/chat.models";
import type { ProgressStage } from "@/models/recommendation.stream.models";

export interface ChatProps {
    message: string;
    onMessageChange: (value: string) => void;
    onSubmit: () => void | Promise<void>;
    isLoading: boolean;
    errorMessage: string | null;
    loadingDetail?: string | null;
    loadingStep?: ProgressStage | null;
    isDestinationResearchLoading?: boolean;
    headerAction?: ReactNode;
    chatRecords: ChatRecordDto[];
    onGoingChatTurn: Partial<ChatRecordDto> | null;
    onRecommendationSelect?: (regionId: string) => void;
}

export interface ChatPromptCardProps {
    message: string;
    onMessageChange: (value: string) => void;
    onSubmit: () => void | Promise<void>;
    isLoading: boolean;
}

export interface ChatConversationProps {
    chatRecords: ChatRecordDto[];
    onGoingChatTurn: Partial<ChatRecordDto> | null;
    isLoading: boolean;
    loadingDetail?: string | null;
    loadingStep?: ProgressStage | null;
    isDestinationResearchLoading?: boolean;
    onRecommendationSelect?: (regionId: string) => void;
}

export interface ChatMessageCardProps {
    turn: ChatRecordDto | Partial<ChatRecordDto>;
    isStreaming?: boolean;
    loadingDetail?: string | null;
    loadingStep?: ProgressStage | null;
    isDestinationResearchLoading?: boolean;
    showTravelDestinationFilter?: boolean;
    showRecommendations?: boolean;
    onRecommendationSelect?: (regionId: string) => void;
}

export interface ChatHeaderActionBarProps {
    headerAction?: ReactNode;
}

export interface ChatConversationPanelProps {
    children: ReactNode;
}

export interface ChatErrorAlertProps {
    errorMessage: string | null;
}

export interface ChatPromptFooterProps {
    children: ReactNode;
}
