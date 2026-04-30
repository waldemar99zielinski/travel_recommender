import { useCallback } from "react";

import type { HealthResponseDto } from "@/models/health.models";
import { fetchHealth } from "@/shared/api/health.api";
import type { HealthContextValue } from "@/shared/context/health/healthContext";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useHealthContextValue(): HealthContextValue {
    const request = useCallback(async () => {
        return fetchHealth();
    }, []);
    const [data, status, error, fetch] = useApiRequest<
        HealthResponseDto
    >(request, {
        requestName: "health",
    });

    const isOperational = data?.status === "ok";

    return {
        data,
        status,
        error,
        fetch,
        isOperational,
    }
}
