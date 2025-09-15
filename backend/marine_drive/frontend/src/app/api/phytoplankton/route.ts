import { NextResponse } from "next/server";
import { getData, setData } from "@/server/phytoplankton/store";

export async function GET() {
  return NextResponse.json(getData());
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as unknown;
    if (!Array.isArray(body)) {
      return NextResponse.json({ error: "Expected an array" }, { status: 400 });
    }

    const data = body
      .map((item: Record<string, unknown>) => ({
        phytoplanktonscientificName: String(
          item?.phytoplanktonscientificName ??
            item?.scientificName ??
            item?.name ??
            ""
        ),
        "no of that pyhtoplankon": isNaN(Number(item?.["no of that pyhtoplankon"]))
          ? String(item?.["no of that pyhtoplankon"] ?? item?.count ?? "0")
          : Number(item?.["no of that pyhtoplankon"]) ??
            Number(item?.count) ??
            0,
        Confidence: isNaN(Number(item?.Confidence))
          ? String(item?.Confidence ?? "0")
          : Number(item?.Confidence) ?? 0,
      }))
      .filter((x) => x.phytoplanktonscientificName);

    setData(data);
    return NextResponse.json({ ok: true, count: getData().length });
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
}
