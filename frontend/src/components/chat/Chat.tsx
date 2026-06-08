import { Card, Stack } from "@mui/material";

import type { ChatProps } from "@/components/chat/Chat.interfaces";
import { ChatConversation } from "@/components/chat/components/ChatConversation";
import { ChatConversationPanel } from "@/components/chat/components/ChatConversationPanel";
import { ChatErrorAlert } from "@/components/chat/components/ChatErrorAlert";
import { ChatHeaderActionBar } from "@/components/chat/components/ChatHeaderActionBar";
import { ChatPromptCard } from "@/components/chat/components/ChatPromptCard";
import { ChatPromptFooter } from "@/components/chat/components/ChatPromptFooter";


export function Chat(props: ChatProps) {
    const {
        chatRecords,
        onGoingChatTurn,
        message,
        onMessageChange,
        onSubmit,
        isLoading,
        errorMessage,
        loadingDetail,
        headerAction,
    } = props;

    return (
        <Stack
            sx={{
                width: { xs: "100%", lg: 380 },
                flexShrink: 0,
                minHeight: { xs: 420, lg: "100%" },
            }}
        >
            <Card
                variant="outlined"
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    flex: 1,
                    minHeight: 0,
                    overflow: "hidden",
                }}
            >
                <ChatHeaderActionBar headerAction={headerAction} />
                <ChatConversationPanel>
                    <ChatConversation
                        chatRecords={chatRecords}
                        onGoingChatTurn={onGoingChatTurn}
                        isLoading={isLoading}
                        loadingDetail={loadingDetail}
                    />
                </ChatConversationPanel>
                <ChatErrorAlert errorMessage={errorMessage} />
                <ChatPromptFooter>
                    <ChatPromptCard
                        message={message}
                        onMessageChange={onMessageChange}
                        onSubmit={onSubmit}
                        isLoading={isLoading}
                    />
                </ChatPromptFooter>
            </Card>
        </Stack>
    );
}
