import {
  LiveFeed,
  TopSpecies,
  DetectionSummary,
  AreaConcentration,
  SampleVolume,
  WaterPH,
  Temperature,
  DissolvedOxygen,
  AlertCard,
} from "@/components/live-feed";

export default function LiveFeedAnalysisPage() {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] p-4">
      <div className="mx-auto">
        {/* Header - more compact */}
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-[var(--foreground)] mb-1">
            Live Feed Analysis
          </h1>
          <p className="text-sm text-[var(--muted)]">
            Real-time monitoring and analysis of marine phytoplankton
          </p>
        </div>

        {/* Bento Grid Layout - taller and better spaced */}
  <div className="grid grid-cols-6 grid-rows-5 gap-4 h-[calc(100vh-140px)]">
          {/* Live Feed - 2x2 */}
          <div className="col-span-2 row-span-2">
            <LiveFeed />
          </div>

          {/* Top Species - 1x2 */}
          <div className="col-span-1 row-span-2">
            <TopSpecies />
          </div>

          {/* Detection Summary - 3x2 */}
          <div className="col-span-3 row-span-2">
            <DetectionSummary />
          </div>

          {/* Row 3 environmental metrics & alert */}
          <div className="col-span-1 row-span-1"><AreaConcentration /></div>
          <div className="col-span-1 row-span-1"><SampleVolume /></div>
          <div className="col-span-1 row-span-1"><WaterPH /></div>
          <div className="col-span-2 row-span-1"><Temperature /></div>
          <div className="col-span-1 row-span-1"><AlertCard /></div>

          {/* Row 4 additional metric(s) */}
          <div className="col-span-1 row-span-1"><DissolvedOxygen /></div>
          <div className="col-span-1 row-span-1"><div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3 flex items-center justify-center text-[10px] text-[var(--muted)]">Reserved</div></div>
          <div className="col-span-1 row-span-1"><div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3 flex items-center justify-center text-[10px] text-[var(--muted)]">Reserved</div></div>
          <div className="col-span-1 row-span-1"><div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3 flex items-center justify-center text-[10px] text-[var(--muted)]">Reserved</div></div>
          <div className="col-span-1 row-span-1"><div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3 flex items-center justify-center text-[10px] text-[var(--muted)]">Reserved</div></div>
        </div>
      </div>
    </div>
  );
}