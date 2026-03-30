import type { ReactNode } from "react";

import { Box, Stack } from "@mui/material";

type RecommendationLayoutProps = {
    chat: ReactNode;
    map: ReactNode;
};

export function RecommendationLayout({ chat, map }: RecommendationLayoutProps) {
    return (
        <Box
            sx={{
                p: { xs: 2, md: 3 },
                height: "100%",
                boxSizing: "border-box",
            }}
        >
            <Stack
                direction={{ xs: "column", lg: "row" }}
                spacing={2}
                sx={{ height: "100%" }}
            >
                {map}
                {chat}
            </Stack>
        </Box>
    );
}
