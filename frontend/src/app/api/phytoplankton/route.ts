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
      .map((item: Record<string, unknown>) => {
        const rec = item as Record<string, unknown>;

        const getFirst = (keys: string[]) => {
          for (const k of keys) if (rec[k] !== undefined) return rec[k];
          return undefined;
        };
        const toNumber = (v: unknown): number | undefined => {
          if (typeof v === "number") return isFinite(v) ? v : undefined;
          if (typeof v === "string") {
            const trimmed = v.trim();
            const n1 = Number(trimmed);
            if (!isNaN(n1)) return n1;
            const n2 = Number(trimmed.replace(/[^\d.+-]/g, ""));
            return isNaN(n2) ? undefined : n2;
          }
          return undefined;
        };

        const name = String(
          getFirst(["phytoplanktonscientificName", "scientificName", "name"]) ?? ""
        );

        const countRaw = getFirst(["no of that pyhtoplankon", "count", "n", "cells"]);
        const countNum = toNumber(countRaw);
        const count = countNum === undefined ? String(countRaw ?? "0") : countNum;

        const confRaw = getFirst(["Confidence", "confidence"]);
        const confNum = toNumber(confRaw);
        const Confidence = confNum === undefined ? (confRaw === undefined ? undefined : String(confRaw)) : confNum;

        const phCandidate = getFirst([
          "optimalPh",
          "optimal_pH",
          "optimalpH",
          "optimal_ph",
          "optimumPh",
          "pH",
          "ph",
        ]);
        const phNum = toNumber(phCandidate);
        const optimalPh = phCandidate === undefined ? undefined : (phNum === undefined ? String(phCandidate) : phNum);

        const tempCandidate = getFirst([
          "optimalTemp",
          "optimalTemperature",
          "optimumTemp",
          "optimumTemperature",
          "temperatureOptimum",
          "tempOptimum",
          "temp",
          "Temp",
        ]);
        const tempNum = toNumber(tempCandidate);
        const optimalTemp = tempCandidate === undefined ? undefined : (tempNum === undefined ? String(tempCandidate) : tempNum);

        let photosyntheticVal = getFirst(["photosynthetic"]);
        if (typeof photosyntheticVal === "string") {
          const l = photosyntheticVal.toLowerCase();
          photosyntheticVal = l === "true" || l === "1" || l === "yes";
        }
        const photosynthetic = typeof photosyntheticVal === "boolean" ? photosyntheticVal : undefined;

        const alertLevel = getFirst(["alertLevel"]) as string | undefined;

  const areaRaw = getFirst(["Area_Concentration", "area_concentration", "areaConc", "area", "AreaConc"]);
  const areaNum = toNumber(areaRaw);
  const Area_Concentration = areaRaw === undefined ? undefined : (areaNum === undefined ? String(areaRaw) : areaNum);

  const volRaw = getFirst(["Sample_Volume", "sample_volume", "volume", "Volume", "sampleVol"]);
  const volNum = toNumber(volRaw);
  const Sample_Volume = volRaw === undefined ? undefined : (volNum === undefined ? String(volRaw) : volNum);

  const doRaw = getFirst(["Dissolved_Oxygen", "dissolved_oxygen", "DO", "do", "oxygen"]);
  const doNum = toNumber(doRaw);
  const Dissolved_Oxygen = doRaw === undefined ? undefined : (doNum === undefined ? String(doRaw) : doNum);

        return {
          phytoplanktonscientificName: name,
          "no of that pyhtoplankon": count,
          Confidence,
          optimalPh,
          optimalTemp,
          photosynthetic,
          alertLevel,
          Area_Concentration,
          Sample_Volume,
            Dissolved_Oxygen,
        };
      })
      .filter((x) => x.phytoplanktonscientificName);

    setData(data);
    return NextResponse.json({ ok: true, count: getData().length });
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
}
