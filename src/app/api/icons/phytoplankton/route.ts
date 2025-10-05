import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const dir = path.join(process.cwd(), "public", "pytoplanktonSvg");
    let files: string[] = [];
    try {
      files = fs.readdirSync(dir).filter((f) => f.toLowerCase().endsWith(".svg"));
    } catch {
      files = [];
    }
    return NextResponse.json({ files });
  } catch (e) {
    return NextResponse.json({ files: [] }, { status: 200 });
  }
}
