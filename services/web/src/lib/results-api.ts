/**
 * Server-side API utilities for fetching screening results.
 *
 * These functions run on the Next.js server and call the FastAPI backend.
 */

import type { ScreeningResult } from "~/types/screening";
import type { ResultMetadata } from "~/types/results";

const AI_SERVICE_URL = process.env.AI_SERVICE_URL ?? "http://ai:5001";

export async function fetchResultsList(): Promise<ResultMetadata[]> {
  const response = await fetch(`${AI_SERVICE_URL}/screening/results`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch results list: ${response.statusText}`);
  }

  return response.json() as Promise<ResultMetadata[]>;
}

export async function fetchResultById(id: string): Promise<ScreeningResult> {
  const response = await fetch(`${AI_SERVICE_URL}/screening/results/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Result not found");
    }
    throw new Error(`Failed to fetch result: ${response.statusText}`);
  }

  return response.json() as Promise<ScreeningResult>;
}
