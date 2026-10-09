import { NextResponse } from "next/server"
import { feedEvents } from "@/lib/dataset"

export const dynamic = "force-dynamic"

/**
 * GET /api/v1/feed — the flight board's event source.
 * There is no live WebSocket backend, so this serves the 373 runnable eval
 * cases in block order. The client replays them on a timer and labels the
 * board REPLAY. Every event is a real historical case with its real verdict.
 */
export async function GET(){
  return NextResponse.json({ mode: "replay", events: feedEvents() })
}
