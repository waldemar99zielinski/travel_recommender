import { useCallback, useMemo, useState } from "react";

import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";
import { createLogger } from "@/shared/lib";

interface UseApiRequestOptions {
    requestName?: string;
}

export function useApiRequest<TData, TArgs = void>(
    request: (args?: TArgs) => Promise<TData>,
    options: UseApiRequestOptions = {},
): ApiHookTuple<TData, TArgs> {
    const [data, setData] = useState<TData | null>(null);
    const [status, setStatus] = useState<FetchStatus>("idle");
    const [error, setError] = useState<string | null>(null);
    const logger = useMemo(
        () =>
            createLogger({
                scope:
                    options.requestName == null
                        ? "useApiRequest"
                        : `useApiRequest:${options.requestName}`,
            }),
        [options.requestName],
    );

    const triggerFetch = useCallback(
        async (args?: TArgs): Promise<TData | null> => {
            setStatus("loading");
            setError(null);
            logger.trace("Request started");

            try {
                const result = await request(args);
                setData(result);
                setStatus("success");
                logger.debug("Request succeeded");

                return result;
            } catch (requestError) {
                const message =
                    requestError instanceof Error
                        ? requestError.message
                        : "Request failed";
                setError(message);
                setStatus("error");
                logger.error("Request failed", requestError);

                return null;
            }
        },
        [logger, request],
    );

    return [data, status, error, triggerFetch];
}
