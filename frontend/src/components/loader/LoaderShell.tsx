import type { ReactNode } from "react";

import { Box, Stack, Typography } from "@mui/material";

type LoaderShellProps = {
    label?: string;
    children: ReactNode;
};

export function LoaderShell({ label, children }: LoaderShellProps) {
    return (
        <Stack alignItems="center" spacing={1.25}>
            <Box
                sx={{
                    position: "relative",
                    minWidth: 116,
                    px: 2,
                    py: 1.75,
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                    bgcolor: "background.paper",
                    display: "flex",
                    justifyContent: "center",
                    overflow: "hidden",
                    "&::before": {
                        content: '""',
                        position: "absolute",
                        inset: -22,
                        background:
                            "radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.16), transparent 56%), radial-gradient(circle at 82% 78%, rgba(15, 118, 110, 0.16), transparent 54%)",
                        pointerEvents: "none",
                    },
                }}
            >
                <Box sx={{ position: "relative", zIndex: 1 }}>{children}</Box>
            </Box>
            {label != null && (
                <Typography variant="body2" color="text.secondary">
                    {label}
                </Typography>
            )}
        </Stack>
    );
}
