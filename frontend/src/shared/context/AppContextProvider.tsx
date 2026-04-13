import { useMemo, type ReactNode } from "react";

import { AppContext, type AppContextValue } from "@/shared/context/appContext";
import { RecommendationContextProvider } from "@/shared/context/recommendation/RecommendationContextProvider";
import { useRecommendationContextValue } from "@/shared/context/recommendation/useRecommendationContextValue";
import { UserContextProvider } from "@/shared/context/user/UserContextProvider";
import { useUserContextValue } from "@/shared/context/user/useUserContextValue";

type AppContextProviderProps = {
    children: ReactNode;
};

export function AppContextProvider({ children }: AppContextProviderProps) {
    const recommendation = useRecommendationContextValue();
    const user = useUserContextValue();

    const value = useMemo<AppContextValue>(
        () => ({
            recommendation,
            user,
        }),
        [recommendation, user],
    );

    return (
        <AppContext.Provider value={value}>
            <UserContextProvider value={user}>
                <RecommendationContextProvider value={recommendation}>
                    {children}
                </RecommendationContextProvider>
            </UserContextProvider>
        </AppContext.Provider>
    );
}
