import { useRef, useState } from "react";

import {
    Box,
    ClickAwayListener,
    Paper,
    Popper,
    Typography,
} from "@mui/material";
import BackHand from "@mui/icons-material/BackHand";
import HighlightAlt from "@mui/icons-material/HighlightAlt";
import { useTranslation } from "react-i18next";

import type { MapInteractionMode } from "@/components/map/Map.interfaces";

interface MapModeSelectorProps {
    mode: MapInteractionMode;
    onChange: (mode: MapInteractionMode) => void;
}

export function MapModeSelector({ mode, onChange }: MapModeSelectorProps) {
    const { t } = useTranslation();
    const [menuOpen, setMenuOpen] = useState(false);
    const anchorRef = useRef<HTMLDivElement | null>(null);

    return (
        <ClickAwayListener onClickAway={() => setMenuOpen(false)}>
            <Box sx={{ position: "relative" }} ref={anchorRef}>
                <Box
                    onClick={() => setMenuOpen((prev) => !prev)}
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 30,
                        height: 30,
                        cursor: "pointer",
                        bgcolor: "#ffffff",
                        borderRadius: 0.2,
                        boxShadow: "0 0 0 2px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1)",
                        lineHeight: 0,
                        padding: 0,
                        outline: "none",
                        "&:hover": { bgcolor: "#f4f4f4" },
                    }}
                >
                    {mode === "browse" ? (
                        <BackHand sx={{ fontSize: 22 }} />
                    ) : (
                        <HighlightAlt sx={{ fontSize: 22 }} />
                    )}
                </Box>
                <Popper
                    open={menuOpen}
                    anchorEl={anchorRef.current}
                    placement="right-start"
                    sx={{ zIndex: 1300 }}
                >
                    <Paper
                        sx={{
                            bgcolor: "#fff",
                            boxShadow: "0 1px 5px rgba(0,0,0,0.4)",
                            borderRadius: 0.4,
                            minWidth: 120,
                            overflow: "hidden",
                            ml: "1rem",
                        }}
                    >
                        <Box
                            onClick={() => {
                                onChange("browse");
                                setMenuOpen(false);
                            }}
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1.5,
                                px: 1.5,
                                py: 1,
                                cursor: "pointer",
                                color: mode === "browse" ? "#333" : "#666",
                                bgcolor: mode === "browse" ? "#f0f0f0" : "transparent",
                                borderBottom: "1px solid #ccc",
                                "&:hover": { bgcolor: "#f4f4f4" },
                            }}
                        >
                                    <BackHand sx={{ fontSize: 18 }} />
                                    <Typography variant="body2">{t("map.mode.browse")}</Typography>
                        </Box>
                        <Box
                            onClick={() => {
                                onChange("selecting-for-recommendation");
                                setMenuOpen(false);
                            }}
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1.5,
                                px: 1.5,
                                py: 1,
                                cursor: "pointer",
                                color: mode === "selecting-for-recommendation" ? "#333" : "#666",
                                bgcolor: mode === "selecting-for-recommendation" ? "#f0f0f0" : "transparent",
                                "&:hover": { bgcolor: "#f4f4f4" },
                            }}
                        >
                                    <HighlightAlt sx={{ fontSize: 21 }} />
                                    <Typography variant="body2">{t("map.mode.select")}</Typography>
                        </Box>
                    </Paper>
                </Popper>
            </Box>
        </ClickAwayListener>
    );
}
