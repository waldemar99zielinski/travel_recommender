import { createContext } from "react";

import type { HealthResponseDto } from "@/models/health.models";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export interface HealthContextValue {
    data: HealthResponseDto | null;
    status: FetchStatus;
    error: string | null;
    fetch: () => Promise<HealthResponseDto | null>;
    isOperational: boolean;
}

export const HealthContext =
    createContext<HealthContextValue | undefined>(undefined);
