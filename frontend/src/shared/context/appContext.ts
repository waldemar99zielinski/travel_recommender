import { createContext } from "react";

export type AppContextValue = Record<string, never>;

export const AppContext = createContext<AppContextValue | undefined>(undefined);
