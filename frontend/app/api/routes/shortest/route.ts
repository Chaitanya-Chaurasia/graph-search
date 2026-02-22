import { NextRequest, NextResponse } from "next/server";
import { ShortestResponseSchema } from "@/models/schemas";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const res = await fetch(`${BACKEND_URL}/routes/shortest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const detail = await res.text();
    return NextResponse.json(
      { error: detail },
      { status: res.status }
    );
  }

  const data = await res.json();
  const validated = ShortestResponseSchema.parse(data);
  return NextResponse.json(validated);
}
