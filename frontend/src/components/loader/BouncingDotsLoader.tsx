import { Box } from "@mui/material";

type BouncingDotsLoaderProps = {
    dotSize?: number;
};

export function BouncingDotsLoader({ dotSize = 10 }: BouncingDotsLoaderProps) {
    return (
        <Box
            sx={{
                display: "flex",
                alignItems: "flex-end",
                gap: 0.75,
                "@keyframes dotBounce": {
                    "0%, 80%, 100%": {
                        transform: "translateY(0)",
                        opacity: 0.45,
                    },
                    "40%": {
                        transform: "translateY(-7px)",
                        opacity: 1,
                    },
                },
            }}
        >
            {[0, 1, 2].map((dot) => (
                <Box
                    key={dot}
                    sx={{
                        width: dotSize,
                        height: dotSize,
                        borderRadius: "50%",
                        bgcolor: dot === 1 ? "primary.main" : "info.main",
                        animation: "dotBounce 0.9s ease-in-out infinite",
                        animationDelay: `${dot * 0.12}s`,
                        boxShadow: "0 3px 8px rgba(15, 23, 42, 0.12)",
                    }}
                />
            ))}
        </Box>
    );
}
