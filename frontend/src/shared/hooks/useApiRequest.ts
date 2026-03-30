import { useCallback, useState } from "react";

import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export function useApiRequest<TData, TArgs = void>(
    request: (args?: TArgs) => Promise<TData>,
): ApiHookTuple<TData, TArgs> {
    const [data, setData] = useState<TData | null>(null);
    const [status, setStatus] = useState<FetchStatus>("idle");
    const [error, setError] = useState<string | null>(null);

    const triggerFetch = useCallback(
        async (args?: TArgs): Promise<TData | null> => {
            setStatus("loading");
            setError(null);

            try {
                const result = await request(args);
                setData(result);
                setStatus("success");

                return result;
            } catch (requestError) {
                const message =
                    requestError instanceof Error
                        ? requestError.message
                        : "Request failed";
                setError(message);
                setStatus("error");

                return null;
            }
        },
        [request],
    );

    return [data, status, error, triggerFetch];
}
