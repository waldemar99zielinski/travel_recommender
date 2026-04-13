import { appConfiguration } from "@/shared/configuration";
import { browserStorage } from "@/shared/storage";

export type LogLevel = "trace" | "debug" | "info" | "warn" | "error" | "silent";

export interface LoggerColors {
    trace: string;
    debug: string;
    info: string;
    warn: string;
    error: string;
}

export interface LoggerOptions {
    scope?: string;
    level?: LogLevel;
    colors?: Partial<LoggerColors>;
    includeTimestamp?: boolean;
}

export interface Logger {
    trace: (message?: unknown, ...args: unknown[]) => void;
    debug: (message?: unknown, ...args: unknown[]) => void;
    info: (message?: unknown, ...args: unknown[]) => void;
    warn: (message?: unknown, ...args: unknown[]) => void;
    error: (message?: unknown, ...args: unknown[]) => void;
    child: (scope: string) => Logger;
    setLevel: (level: LogLevel) => void;
    getLevel: () => LogLevel;
}

const LOG_LEVEL_PRIORITY: Readonly<Record<LogLevel, number>> = {
    trace: 10,
    debug: 20,
    info: 30,
    warn: 40,
    error: 50,
    silent: Number.POSITIVE_INFINITY,
};

const DEFAULT_LOG_COLORS: Readonly<LoggerColors> = {
    trace: "#7f8c8d",
    debug: "#2980b9",
    info: "#16a085",
    warn: "#d35400",
    error: "#c0392b",
};

const LOG_LEVEL_STORAGE_KEY = "hybrid:logger:base-level";
const DEFAULT_BASE_LOG_LEVEL: LogLevel =
    appConfiguration.environment === "dev" ? "trace" : "info";

const CONSOLE_METHOD_BY_LEVEL: Readonly<
    Record<Exclude<LogLevel, "silent">, "log" | "debug" | "info" | "warn" | "error">
> = {
    trace: "log",
    debug: "debug",
    info: "info",
    warn: "warn",
    error: "error",
};

function isLogLevel(value: string | null): value is LogLevel {
    if (value == null) {
        return false;
    }

    return value in LOG_LEVEL_PRIORITY;
}

function readStoredBaseLogLevel(): LogLevel | null {
    const value = browserStorage.getItem(LOG_LEVEL_STORAGE_KEY);
    if (!isLogLevel(value)) {
        return null;
    }

    return value;
}

function persistBaseLogLevel(level: LogLevel): void {
    browserStorage.setItem(LOG_LEVEL_STORAGE_KEY, level);
}

let baseLogLevel: LogLevel = readStoredBaseLogLevel() ?? DEFAULT_BASE_LOG_LEVEL;

if (typeof window !== "undefined") {
    window.addEventListener("storage", (event) => {
        if (event.key !== LOG_LEVEL_STORAGE_KEY) {
            return;
        }

        if (isLogLevel(event.newValue)) {
            baseLogLevel = event.newValue;
            return;
        }

        if (event.newValue == null) {
            baseLogLevel = DEFAULT_BASE_LOG_LEVEL;
        }
    });
}

function shouldLog(level: Exclude<LogLevel, "silent">, currentLevel: LogLevel): boolean {
    if (currentLevel === "silent") {
        return false;
    }

    return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[currentLevel];
}

function formatPrefix(level: Exclude<LogLevel, "silent">, scope?: string, includeTimestamp?: boolean): string {
    const segments: string[] = [level.toUpperCase()];

    if (scope != null && scope.length > 0) {
        segments.push(scope);
    }

    if (includeTimestamp ?? true) {
        segments.unshift(new Date().toISOString());
    }

    return `[${segments.join("] [")}]`;
}

function getConsoleMethod(level: Exclude<LogLevel, "silent">): (...data: unknown[]) => void {
    const methodName = CONSOLE_METHOD_BY_LEVEL[level];
    return console[methodName].bind(console);
}

function mergeScopes(parentScope?: string, childScope?: string): string | undefined {
    if (parentScope == null || parentScope.length === 0) {
        return childScope;
    }

    if (childScope == null || childScope.length === 0) {
        return parentScope;
    }

    return `${parentScope}:${childScope}`;
}

export function getBaseLogLevel(): LogLevel {
    return baseLogLevel;
}

export function setBaseLogLevel(level: LogLevel): void {
    baseLogLevel = level;
    persistBaseLogLevel(level);
}

export function clearStoredBaseLogLevel(): void {
    browserStorage.removeItem(LOG_LEVEL_STORAGE_KEY);
    baseLogLevel = DEFAULT_BASE_LOG_LEVEL;
}

export function createLogger(options: LoggerOptions = {}): Logger {
    const colors: LoggerColors = {
        ...DEFAULT_LOG_COLORS,
        ...options.colors,
    };
    let levelOverride = options.level;

    const logAt = (level: Exclude<LogLevel, "silent">, message?: unknown, ...args: unknown[]) => {
        const activeLevel = levelOverride ?? getBaseLogLevel();
        if (!shouldLog(level, activeLevel)) {
            return;
        }

        const prefix = formatPrefix(level, options.scope, options.includeTimestamp);
        const labelStyle = `color: ${colors[level]}; font-weight: 700;`;
        const resetStyle = "color: inherit; font-weight: inherit;";
        const consoleMethod = getConsoleMethod(level);

        if (typeof message === "string") {
            consoleMethod(`%c${prefix}%c ${message}`, labelStyle, resetStyle, ...args);
            return;
        }

        if (message === undefined) {
            consoleMethod(`%c${prefix}`, labelStyle);
            return;
        }

        consoleMethod(`%c${prefix}`, labelStyle, message, ...args);
    };

    return {
        trace: (message?: unknown, ...args: unknown[]) => {
            logAt("trace", message, ...args);
        },
        debug: (message?: unknown, ...args: unknown[]) => {
            logAt("debug", message, ...args);
        },
        info: (message?: unknown, ...args: unknown[]) => {
            logAt("info", message, ...args);
        },
        warn: (message?: unknown, ...args: unknown[]) => {
            logAt("warn", message, ...args);
        },
        error: (message?: unknown, ...args: unknown[]) => {
            logAt("error", message, ...args);
        },
        child: (scope: string) =>
            createLogger({
                ...options,
                scope: mergeScopes(options.scope, scope),
                level: levelOverride,
            }),
        setLevel: (level: LogLevel) => {
            levelOverride = level;
        },
        getLevel: () => levelOverride ?? getBaseLogLevel(),
    };
}

export const logger = createLogger();
