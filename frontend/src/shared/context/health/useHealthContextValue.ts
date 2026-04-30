import { useCallback } from "react";

import type { HealthResponseDto } from "@/models/health.models";
import { fetchHealth as fetchHealthRequest } from "@/shared/api/health.api";
import type { HealthContextValue } from "@/shared/context/health/healthContext";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useHealthContextValue(): HealthContextValue {
    const request = useCallback(async () => {
        return fetchHealthRequest();
    }, []);
    const [healthData, healthStatus, healthError, fetchHealth] = useApiRequest<
        HealthResponseDto
    >(request, {
        requestName: "health",
    });

    const isOperational = healthData?.status === "ok";

    return {
        healthData,
        healthStatus,
        healthError,
        fetchHealth,
        isOperational,
    };
}
