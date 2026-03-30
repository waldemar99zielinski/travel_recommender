import { createTheme } from "@mui/material/styles";

export const appTheme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#0f766e",
        },
        secondary: {
            main: "#fb923c",
        },
        background: {
            default: "#f8fafc",
            paper: "#ffffff",
        },
    },
    shape: {
        borderRadius: 12,
    },
    typography: {
        fontFamily:
            "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
        h3: {
            fontWeight: 700,
        },
    },
});
