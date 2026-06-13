import { useEffect, useState } from "react";

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
import { TimedProgressLoader } from "@/components/loader/TimedProgressLoader";
import { MapLegend } from "@/components/map/components/MapLegend";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import { TravelMapLoader } from "@/components/loader/TravelMapLoader";
import type { ChatRecordDto } from "@/models/chat.models";
import { appConfiguration } from "@/shared/configuration";
import { createLogger } from "@/shared/lib";

const testPageLogger = createLogger({ scope: "TestPage" });

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
        <Stack direction="row" spacing={0.75} useFlexGap sx={{ flexWrap: "wrap" }}>
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
    const [chatRecords, setChatRecords] = useState<ChatRecordDto[]>([
        {
            user_id: "demo-user",
            session_id: "demo-session",
            chat_history_number: 0,
            user_request: "",
            system_response: t("test.introMessage"),
            recommendations: [],
            travel_destinations_evaluations: [],
            included_regions_ids: [],
            excluded_regions_ids: [],
        },
        {
            user_id: "demo-user",
            session_id: "demo-session",
            chat_history_number: 1,
            user_request: "",
            system_response: t("test.clickableMessage"),
            recommendations: [],
            travel_destinations_evaluations: [],
            included_regions_ids: [],
            excluded_regions_ids: [],
        },
    ]);

    useEffect(() => {
        testPageLogger.debug("Opened test page", {
            environment: appConfiguration.environment,
            loggerLevel: testPageLogger.getLevel(),
        });

        return () => {
            testPageLogger.trace("Leaving test page");
        };
    }, []);

    const handleSubmit = () => {
        const trimmedMessage = message.trim();
        if (trimmedMessage.length === 0) {
            testPageLogger.debug("Ignored empty message submit");
            return;
        }

        testPageLogger.trace("Submitting demo message", {
            length: trimmedMessage.length,
        });

        setChatRecords((previous) => [
            ...previous,
            {
                user_id: "demo-user",
                session_id: "demo-session",
                chat_history_number: previous.length,
                user_request: trimmedMessage,
                system_response: t("test.demoReply", { message: trimmedMessage }),
                recommendations: [],
                travel_destinations_evaluations: [],
                included_regions_ids: [],
                excluded_regions_ids: [],
            },
        ]);
        setMessage("");
        testPageLogger.debug("Demo message submitted");
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
                            <QuickReplyChips
                                onSelect={(value) => {
                                    setMessage(value);
                                    testPageLogger.debug("Quick reply selected", { value });
                                }}
                            />
                            <Divider />
                            <Chat
                                chatRecords={chatRecords}
                                onGoingChatTurn={null}
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
                            <Stack direction="row" sx={{ alignItems: "center" }} spacing={1}>
                                <Switch
                                    checked={showLoader}
                                    onChange={(event) => {
                                        const nextValue = event.target.checked;
                                        setShowLoader(nextValue);
                                        testPageLogger.debug("Loader preview toggled", {
                                            visible: nextValue,
                                        });
                                    }}
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {t("test.showLoaderPreview")}
                                </Typography>
                            </Stack>
                            {showLoader ? (
                                <Stack spacing={2} sx={{ alignItems: "flex-start" }}>
                                    <TravelMapLoader />
                                    <TimedProgressLoader
                                        label={t("test.timerLoaderLabel")}
                                        durationMs={12000}
                                        initialElapsedMs={3500}
                                    />
                                </Stack>
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
                            <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
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
