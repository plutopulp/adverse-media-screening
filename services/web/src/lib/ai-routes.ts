const AI_BASE_URL = process.env.AI_SERVICE_URL ?? "http://ai:5001";

export const aiRoutes = {
  health: `${AI_BASE_URL}/health`,
  screening: {
    screen: `${AI_BASE_URL}/screening/screen`,
  },
  test: {
    mockResult: (example?: string) =>
      `${AI_BASE_URL}/test/mock-result${example ? `?example=${example}` : ""}`,
  },
} as const;

export interface ScreeningRequest {
  url: string;
  first_name: string;
  last_name: string;
  middle_names?: string;
  date_of_birth?: string; // ISO date string (YYYY-MM-DD)
}
