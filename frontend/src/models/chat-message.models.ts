import { z } from "zod";

export interface ChatTextMessageContextDto {
    text: string;
}

export interface ChatMessageDto {
    type: "text";
    context: ChatTextMessageContextDto;
}

export const chatTextMessageContextDtoSchema = z.object({
    text: z.string(),
}) satisfies z.ZodType<ChatTextMessageContextDto>;

export const chatMessageDtoSchema = z.object({
    type: z.literal("text"),
    context: chatTextMessageContextDtoSchema,
}) satisfies z.ZodType<ChatMessageDto>;
