import { createContext } from "react";

import type { RecommendationContextValue } from "@/shared/context/recommendation/recommendationContext";
import type { UserContextValue } from "@/shared/context/user/userContext";

export interface AppContextValue {
    recommendation: RecommendationContextValue;
    user: UserContextValue;
}

export const AppContext = createContext<AppContextValue | undefined>(undefined);
