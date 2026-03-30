import type { ReactNode } from "react";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
    id: string;
    role: ChatRole;
    content: ReactNode;
    onClick?: () => void;
}

export interface ChatProps {
    messages: ChatMessage[];
    message: string;
    onMessageChange: (value: string) => void;
    onSubmit: () => void;
    isLoading: boolean;
    errorMessage: string | null;
}

export interface ChatPromptCardProps {
    message: string;
    onMessageChange: (value: string) => void;
    onSubmit: () => void;
    isLoading: boolean;
}

export interface ChatConversationProps {
    messages: ChatMessage[];
}

export interface ChatMessageCardProps {
    message: ChatMessage;
}
