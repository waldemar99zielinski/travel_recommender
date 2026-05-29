import { useMemo, type PropsWithChildren } from "react";

import { Box, Button, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { SelectedForRecommendationStatusType } from "@/features/recommendation/context/handlers/useRecommendationMapState";

interface DraftSelectionMenuProps {
    regionSelectedForRecommendationStatus: Map<string, SelectedForRecommendationStatusType>;
    onInclude: () => void;
    onExclude: () => void;
    onClear: () => void;
    onExitSelectionMode: () => void;
}

function DraftSelectionMenuContainer(props: PropsWithChildren<{}>) {
    return  <Box
            sx={{
                position: "absolute",
                bottom: 16,
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 9999,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 1,
                px: 2,
                py: 1.5,
                bgcolor: "background.paper",
                border: 1,
                borderColor: "divider",
                borderRadius: 2,
                boxShadow: 4,
            }}
        >
            {props.children}
        </Box>;
}

export function DraftSelectionMenu({
    regionSelectedForRecommendationStatus,
    onInclude,
    onExclude,
    onClear,
    onExitSelectionMode,
}: DraftSelectionMenuProps) {
    const { t } = useTranslation();
    const draftCount = useMemo(
        () =>
            [...regionSelectedForRecommendationStatus.values()].filter(
                (s) => s === "draft",
            ).length,
        [regionSelectedForRecommendationStatus],
    );

    if (draftCount === 0) {
        return <DraftSelectionMenuContainer>
            <Button
                size="small"
                variant="outlined"
                color="inherit"
                onClick={onExitSelectionMode}
            >
                {t("map.draftSelectionMenu.exitSelectionMode")}
            </Button> 
        </DraftSelectionMenuContainer>;
    }

    return (
        <DraftSelectionMenuContainer>
            <Typography variant="body2" color="text.secondary">
                {t("map.draftSelectionMenu.regionsSelected", { count: draftCount })}
            </Typography>
            <Button
                size="small"
                variant="contained"
                color="success"
                onClick={onInclude}
            >
                {t("map.draftAction.include")}
            </Button>
            <Button
                size="small"
                variant="contained"
                color="error"
                onClick={onExclude}
            >
                {t("map.draftAction.exclude")}
            </Button>
            <Button
                size="small"
                variant="outlined"
                color="inherit"
                onClick={onClear}
            >
                {t("map.draftSelectionMenu.clear")}
            </Button>
        </DraftSelectionMenuContainer>
    );
}
