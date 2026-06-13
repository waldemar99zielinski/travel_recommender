import { z } from "zod";

export interface DestinationItemDto {
    id: string;
    parent_region: string;
    description: string;
}

export interface DestinationListResponseDto {
    destinations: DestinationItemDto[];
    total: number;
}

export const destinationItemDtoSchema = z.object({
    id: z.string(),
    parent_region: z.string(),
    description: z.string(),
}) satisfies z.ZodType<DestinationItemDto>;

export const destinationListResponseDtoSchema = z.object({
    destinations: z.array(destinationItemDtoSchema),
    total: z.number().int().nonnegative(),
}) satisfies z.ZodType<DestinationListResponseDto>;

export function validateDestinationListResponseDto(
    payload: unknown,
): DestinationListResponseDto {
    return destinationListResponseDtoSchema.parse(payload);
}
