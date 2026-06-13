import { type ReactNode } from "react";

import { Box, Fade, IconButton, Paper, SvgIcon, Typography } from "@mui/material";

export interface OverlayPanelProps {
    open: boolean;
    onClose: () => void;
    children: ReactNode;
    width?: number;
    title?: string;
}

export function OverlayPanel({
    open,
    onClose,
    children,
    width = 360,
    title,
}: OverlayPanelProps) {
    return (
        <Box
            sx={{
                position: "absolute",
                inset: 0,
                zIndex: 1000,
                pointerEvents: "none",
            }}
        >
            <Box
                sx={{
                    position: "absolute",
                    top: 0,
                    right: 0,
                    bottom: 0,
                    width,
                    pointerEvents: open ? "auto" : "none",
                    p: 1.5,
                    pl: 0,
                }}
            >
                <Fade in={open} timeout={200} mountOnEnter unmountOnExit>
                    <Paper
                        sx={{
                            height: "100%",
                            borderRadius: 1.5,
                            display: "flex",
                            flexDirection: "column",
                            overflow: "hidden",
                            bgcolor: "background.paper",
                        }}
                        elevation={8}
                    >
                        <Box
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                px: 2,
                                py: 1,
                                flexShrink: 0,
                            }}
                        >
                            {title != null && (
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                    {title}
                                </Typography>
                            )}
                            <IconButton size="small" onClick={onClose} sx={{ ml: "auto" }}>
                                <SvgIcon fontSize="small">
                                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                                </SvgIcon>
                            </IconButton>
                        </Box>
                        <Box
                            sx={{
                                flex: 1,
                                overflow: "auto",
                                px: 2,
                                pb: 2,
                            }}
                        >
                            {children}
                        </Box>
                    </Paper>
                </Fade>
            </Box>
        </Box>
    );
}
