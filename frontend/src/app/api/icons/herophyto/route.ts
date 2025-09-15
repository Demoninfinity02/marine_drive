import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const exts = new Set([".svg", ".png", ".jpg", ".jpeg", ".webp"]);

export async function GET() {
  try {
    const dir = path.join(process.cwd(), "public", "heropytoplanktonimg");
    let files: string[] = [];
    try {
      files = fs
        .readdirSync(dir)
        .filter((f) => exts.has(path.extname(f).toLowerCase()));
    } catch {
      files = [];
    }
    return NextResponse.json({ files });
  } catch {
    return NextResponse.json({ files: [] }, { status: 200 });
  }
}
