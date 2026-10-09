import { NextResponse } from "next/server"
import { datasetHealth } from "@/lib/dataset"

export const dynamic = "force-dynamic"

export async function GET(){
  return NextResponse.json(datasetHealth())
}
