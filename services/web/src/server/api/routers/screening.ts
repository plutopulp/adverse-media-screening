import { z } from "zod";
import * as cheerio from "cheerio";

import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

const getText = async (url: string) => {
  const res = await fetch(url);
  const html = await res.text();

  const $ = cheerio.load(html);

  // const title = $("title").text().trim() || undefined;
  // const description = $('meta[name="description"]').attr("content")?.trim();

  // remove some non-text elements
  $("title").remove();
  $("script").remove();
  $("style").remove();
  $("noscript").remove();
  $("iframe").remove();
  $("audio").remove();
  $("source").remove();
  $("img").remove();
  $("video").remove();

  const text = $("body").text().trim();

  console.log(text);

  return text;
};

const screen = async (url: string, name: string, _dateOfBirth: Date | null) => {
  const text = await getText(url);

  return {
    match: text.toLowerCase().includes(name.toLowerCase()),
    sentiment: "negative",
  };
};

export const screeningRouter = createTRPCRouter({
  checkWebsite: publicProcedure
    .input(
      z.object({
        url: z.string(),
        name: z.string(),
        dateOfBirth: z.string().optional(),
      }),
    )
    .mutation(({ input }) => {
      const dateOfBirth = input.dateOfBirth
        ? new Date(input.dateOfBirth)
        : null;

      return screen(input.url, input.name, dateOfBirth);
    }),
});
