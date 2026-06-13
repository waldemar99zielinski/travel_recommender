const CUSTOM_DELIMITER = "\n\n";

export interface SseEvent {
    event: string;
    data: unknown;
}

export async function* streamSse(
    url: string,
    body: object,
    signal?: AbortSignal,
): AsyncGenerator<SseEvent> {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal,
    });

    if (!response.ok) {
        throw new Error(`SSE request failed with status ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (reader == null) {
        throw new Error("Response body is not readable");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split(CUSTOM_DELIMITER);
        buffer = messages.pop() ?? "";

        for (const message of messages) {
            const parsed = parseSseMessage(message.trim());
            if (parsed != null) {
                yield parsed;
            }
        }
    }
}

function parseSseMessage(message: string): SseEvent | null {
    if (message.length === 0) return null;

    let event = "message";
    let data: string | null = null;

    for (const line of message.split("\n")) {
        if (line.startsWith("event: ")) {
            event = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
            data = line.slice(6);
        }
    }

    if (data == null) return null;

    try {
        return { event, data: JSON.parse(data) };
    } catch {
        return { event, data };
    }
}
