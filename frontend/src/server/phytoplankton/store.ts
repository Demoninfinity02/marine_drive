export type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": string | number;
  Confidence?: string | number;
  optimalPh?: string | number;
  optimalTemp?: string | number;
  photosynthetic?: boolean | string;
  alertLevel?: string;
  Area_Concentration?: string | number;
  Sample_Volume?: string | number;
  Dissolved_Oxygen?: string | number;
};

// Use a global singleton so that multiple route module instances (in dev / edge) share state
const g = globalThis as unknown as {
  __phytoData?: RawPhyto[];
  __phytoSubs?: Set<() => void>;
};

if (!g.__phytoData) g.__phytoData = [];
if (!g.__phytoSubs) g.__phytoSubs = new Set();

export function getData() {
  return g.__phytoData!;
}

export function setData(arr: RawPhyto[]) {
  g.__phytoData = arr;
  // Notify subscribers (SSE streams) to push an update
  for (const fn of g.__phytoSubs!) {
    try { fn(); } catch { /* noop */ }
  }
}

export function subscribe(fn: () => void) {
  g.__phytoSubs!.add(fn);
  return () => {
    g.__phytoSubs!.delete(fn);
  };
}
