import { z } from "zod";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";
import { aiRoutes, type ScreeningRequest } from "~/lib/ai-routes";
import type { ScreeningResult } from "~/types/screening";

const screen = async (payload: ScreeningRequest): Promise<ScreeningResult> => {
  const formData = new FormData();
  formData.append("url", String(payload.url));
  formData.append("first_name", String(payload.first_name));
  formData.append("last_name", String(payload.last_name));
  if (payload.middle_names) {
    formData.append("middle_names", String(payload.middle_names));
  }
  if (payload.date_of_birth) {
    formData.append("date_of_birth", String(payload.date_of_birth));
  }

  const response = await fetch(aiRoutes.screening.screen, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `AI service error (${response.status}): ${errorText || response.statusText}`,
    );
  }

  return response.json() as Promise<ScreeningResult>;
};

export const screeningRouter = createTRPCRouter({
  checkWebsite: publicProcedure
    .input(
      z.object({
        url: z.string().url("Please enter a valid URL"),
        firstName: z.string().min(1, "First name is required"),
        lastName: z.string().min(1, "Last name is required"),
        middleNames: z.string().optional(),
        birthDay: z.number().int().min(1).max(31).optional(),
        birthMonth: z.number().int().min(1).max(12).optional(),
        birthYear: z.number().int().min(1900).max(2030).optional(),
      }),
    )
    .mutation(({ input }) => {
      // Serialize DOB to ISO format if all parts provided
      let dateOfBirth: string | undefined;
      if (input.birthYear && input.birthMonth && input.birthDay) {
        const date = new Date(
          input.birthYear,
          input.birthMonth - 1,
          input.birthDay,
        );
        dateOfBirth = date.toISOString().split("T")[0]; // YYYY-MM-DD
      }

      return screen({
        url: input.url,
        first_name: input.firstName,
        last_name: input.lastName,
        ...(input.middleNames && { middle_names: input.middleNames }),
        ...(dateOfBirth && { date_of_birth: dateOfBirth }),
      });
    }),
});
