import type { ReactNode } from "react";
import type { ChatRecordDto } from "@/models/chat.models";

export interface ChatProps {
    message: string;
    onMessageChange: (value: string) => void;
    onSubmit: () => void | Promise<void>;
    isLoading: boolean;
    errorMessage: string | null;
    loadingDetail?: string | null;
    headerAction?: ReactNode;
    chatRecords: ChatRecordDto[];
    onGoingChatTurn: Partial<ChatRecordDto> | null;
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
}

export interface ChatMessageCardProps {
    turn: ChatRecordDto | Partial<ChatRecordDto>;
    isStreaming?: boolean;
    loadingDetail?: string | null;
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
