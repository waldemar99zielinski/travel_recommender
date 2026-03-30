export type FetchStatus = "idle" | "loading" | "success" | "error";

export type ApiHookTuple<TData, TArgs = void> = [
    data: TData | null,
    status: FetchStatus,
    error: string | null,
    fetch: (args?: TArgs) => Promise<TData | null>,
];
