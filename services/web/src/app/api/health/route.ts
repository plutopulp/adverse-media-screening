// temporary route to check if the ai service is running

import { NextResponse } from "next/server";

export const runtime = "nodejs";
interface HealthResponse {
  message: string;
}

export async function GET() {
  const baseUrl = process.env.AI_SERVICE_URL;
  if (!baseUrl) {
    return NextResponse.json(
      { error: "AI_SERVICE_URL is not configured" },
      { status: 500 },
    );
  }

  const target = `${baseUrl.replace(/\/$/, "")}/health`;

  try {
    const res = await fetch(target, { cache: "no-store" });
    const data = (await res.json().catch(() => ({}))) as HealthResponse;
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(
      { error: "Failed to reach AI service", target },
      { status: 502 },
    );
  }
}
