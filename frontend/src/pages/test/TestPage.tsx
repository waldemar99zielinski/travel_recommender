import { useState } from "react";

import {
    Box,
    Card,
    CardContent,
    Chip,
    Divider,
    Stack,
    Switch,
    Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

import { Chat } from "@/components/chat/Chat";
import { MapLegend } from "@/components/map/components/MapLegend";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import { TravelMapLoader } from "@/components/loader/TravelMapLoader";
import type { ChatMessage } from "@/components/chat/Chat.interfaces";

interface QuickReplyChipsProps {
    onSelect: (value: string) => void;
}

function QuickReplyChips({ onSelect }: QuickReplyChipsProps) {
    const { t } = useTranslation();

    const quickReplies = [
        t("test.quickReplies.warmBeach"),
        t("test.quickReplies.mountainTown"),
        t("test.quickReplies.familyCityBreak"),
    ];

    return (
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap">
            {quickReplies.map((reply) => (
                <Chip
                    key={reply}
                    label={reply}
                    size="small"
                    clickable
                    variant="outlined"
                    onClick={() => onSelect(reply)}
                />
            ))}
        </Stack>
    );
}

export function TestPage() {
    const { t } = useTranslation();
    const [message, setMessage] = useState("");
    const [showLoader, setShowLoader] = useState(true);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
        {
            id: "preset-assistant-intro",
            role: "assistant",
            content: t("test.introMessage"),
        },
        {
            id: "preset-assistant-clickable",
            role: "assistant",
            content: t("test.clickableMessage"),
            onClick: () => {
                setMessage(t("test.clickableAutofill"));
            },
        },
    ]);

    const dynamicMessages: ChatMessage[] = [
        ...chatMessages,
        {
            id: "preset-quick-replies",
            role: "assistant",
            content: (
                <Stack spacing={1}>
                    <Typography variant="body2">{t("test.quickPicks")}</Typography>
                    <QuickReplyChips onSelect={setMessage} />
                </Stack>
            ),
        },
    ];

    const handleSubmit = () => {
        const trimmedMessage = message.trim();
        if (trimmedMessage.length === 0) {
            return;
        }

        setChatMessages((previous) => [
            ...previous,
            {
                id: `user-${Date.now()}`,
                role: "user",
                content: trimmedMessage,
            },
            {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: t("test.demoReply", { message: trimmedMessage }),
            },
        ]);
        setMessage("");
    };

    return (
        <Box
            sx={{
                minHeight: "100%",
                px: { xs: 2, md: 3 },
                py: { xs: 2, md: 3 },
                bgcolor: "background.default",
            }}
        >
            <Stack spacing={2.5} sx={{ maxWidth: 980, mx: "auto" }}>
                <Stack spacing={0.5}>
                    <Typography variant="h4">{t("test.pageTitle")}</Typography>
                    <Typography color="text.secondary">
                        {t("test.pageDescription")}
                    </Typography>
                </Stack>

                <Card variant="outlined">
                    <CardContent>
                        <Stack spacing={2}>
                            <Typography variant="h6">
                                {t("test.chatPreviewTitle")}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {t("test.chatPreviewDescription")}
                            </Typography>
                            <Divider />
                            <Chat
                                messages={dynamicMessages}
                                message={message}
                                onMessageChange={setMessage}
                                onSubmit={handleSubmit}
                                isLoading={false}
                                errorMessage={null}
                            />
                        </Stack>
                    </CardContent>
                </Card>

                <Card variant="outlined">
                    <CardContent>
                        <Stack spacing={2}>
                            <Stack direction="row" alignItems="center" spacing={1}>
                                <Switch
                                    checked={showLoader}
                                    onChange={(event) =>
                                        setShowLoader(event.target.checked)
                                    }
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {t("test.showLoaderPreview")}
                                </Typography>
                            </Stack>
                            {showLoader ? (
                                <TravelMapLoader />
                            ) : (
                                <Typography color="text.secondary">
                                    {t("test.loaderHidden")}
                                </Typography>
                            )}
                        </Stack>
                    </CardContent>
                </Card>

                <Card variant="outlined">
                    <CardContent>
                        <Stack spacing={1.5}>
                            <Typography variant="h6">
                                {t("test.mapSnippetsTitle")}
                            </Typography>
                            <Stack direction="row" spacing={1.5} alignItems="center">
                                <Typography variant="body2" color="text.secondary">
                                    {t("test.rankLabelExample")}
                                </Typography>
                                <MapRankLabel rank={1} score={92} mode="rank-score" />
                            </Stack>
                            <Box
                                sx={{
                                    position: "relative",
                                    minHeight: 120,
                                    borderRadius: 2,
                                    border: "1px dashed",
                                    borderColor: "divider",
                                    bgcolor: "rgba(15, 23, 42, 0.04)",
                                }}
                            >
                                <MapLegend />
                            </Box>
                        </Stack>
                    </CardContent>
                </Card>
            </Stack>
        </Box>
    );
}
