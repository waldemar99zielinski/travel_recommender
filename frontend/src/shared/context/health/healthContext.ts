import { createContext } from "react";

import type { HealthResponseDto } from "@/models/health.models";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export interface HealthContextValue {
    healthData: HealthResponseDto | null;
    healthStatus: FetchStatus;
    healthError: string | null;
    fetchHealth: () => Promise<HealthResponseDto | null>;
    isOperational: boolean;
}

export const HealthContext =
    createContext<HealthContextValue | undefined>(undefined);
