import { useMemo, useState } from "react";

import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Chip,
    Stack,
    SvgIcon,
    Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

import type {
    TravelDestinationFilter,
    TravelDestinationRegionFilter,
} from "@/models/recommendation.stream.models";

interface TravelDestinationFilterDisplayProps {
    filter: TravelDestinationFilter;
}

function RegionFilterChips({
    label,
    filters,
}: {
    label: string;
    filters: TravelDestinationRegionFilter[];
}) {
    if (filters.length === 0) return null;

    return (
        <Stack spacing={0.5}>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
                {label}
            </Typography>
            <Stack direction="row" spacing={0.5} useFlexGap sx={{ flexWrap: "wrap" }}>
                {filters.map((filter, idx) => (
                    <Chip
                        key={idx}
                        label={filter.region_name}
                        size="small"
                        color={filter.type === "include" ? "success" : "error"}
                        variant="outlined"
                    />
                ))}
            </Stack>
        </Stack>
    );
}

export function TravelDestinationFilterDisplay({
    filter,
}: TravelDestinationFilterDisplayProps) {
    const { t } = useTranslation();
    const [expanded, setExpanded] = useState(false);

    const summaryParts = useMemo(() => {
        const parts: string[] = [];

        const regionCount = filter.parent_region_filters?.length ?? 0;
        if (regionCount > 0) {
            parts.push(t("chat.filterSummary.regions", { count: regionCount }));
        }

        if (filter.seasonality?.season) {
            parts.push(filter.seasonality.season);
        }

        if (filter.budget?.cost_term?.inferred_level) {
            parts.push(filter.budget.cost_term.inferred_level);
        }

        return parts;
    }, [filter, t]);

    const hasContent =
        (filter.parent_region_filters?.length ?? 0) > 0 ||
        filter.seasonality != null ||
        filter.budget != null;

    if (!hasContent) {
        return null;
    }

    return (
        <Accordion
            expanded={expanded}
            onChange={(_, nextExpanded) => setExpanded(nextExpanded)}
            disableGutters
            elevation={0}
            square
            sx={{
                border: "1px solid",
                borderColor: "primary.light",
                borderRadius: 1.5,
                overflow: "hidden",
                bgcolor: "action.hover",
                "&:before": { display: "none" },
            }}
        >
            <AccordionSummary
                expandIcon={
                    <SvgIcon fontSize="small" viewBox="0 0 24 24">
                        <path d="m7 10 5 5 5-5z" />
                    </SvgIcon>
                }
                sx={{
                    px: 1.25,
                    minHeight: 0,
                    "& .MuiAccordionSummary-content": { my: 1 },
                }}
            >
                <Stack
                    direction="row"
                    spacing={1}
                    sx={{ width: "100%", minWidth: 0, alignItems: "center" }}
                >
                    <SvgIcon fontSize="small" color="primary">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                    </SvgIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, flex: 1 }}>
                        {t("chat.filterSummary.detectedFilters")}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        {summaryParts.join(" · ")}
                    </Typography>
                </Stack>
            </AccordionSummary>
            <AccordionDetails sx={{ px: 1.25, pt: 0, pb: 1.25 }}>
                <Stack spacing={1.5}>
                    {filter.parent_region_filters != null &&
                        filter.parent_region_filters.length > 0 && (
                            <RegionFilterChips
                                label={t("chat.filterSummary.parentRegions")}
                                filters={filter.parent_region_filters}
                            />
                        )}
                    {filter.seasonality != null &&
                        (filter.seasonality.season || filter.seasonality.months) && (
                            <Stack spacing={0.5}>
                                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                    {t("chat.filterSummary.seasonality")}
                                </Typography>
                                <Stack
                                    direction="row"
                                    spacing={0.5}
                                    useFlexGap
                                    sx={{ flexWrap: "wrap" }}
                                >
                                    {filter.seasonality.season && (
                                        <Chip
                                            label={filter.seasonality.season}
                                            size="small"
                                            color="info"
                                            variant="outlined"
                                        />
                                    )}
                                    {filter.seasonality.months?.map((month) => (
                                        <Chip
                                            key={month}
                                            label={month}
                                            size="small"
                                            variant="outlined"
                                        />
                                    ))}
                                </Stack>
                            </Stack>
                        )}
                    {filter.budget != null &&
                        (filter.budget.min_cost_per_week != null ||
                            filter.budget.max_cost_per_week != null ||
                            filter.budget.cost_term != null) && (
                            <Stack spacing={0.5}>
                                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                                    {t("chat.filterSummary.budget")}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {filter.budget.cost_term?.inferred_level &&
                                        `${filter.budget.cost_term.inferred_level}`}
                                    {filter.budget.min_cost_per_week != null &&
                                        ` from ${filter.budget.min_cost_per_week}/week`}
                                    {filter.budget.max_cost_per_week != null &&
                                        ` up to ${filter.budget.max_cost_per_week}/week`}
                                </Typography>
                            </Stack>
                        )}
                </Stack>
            </AccordionDetails>
        </Accordion>
    );
}
