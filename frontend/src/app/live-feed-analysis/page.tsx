import {
  LiveFeed,
  TopSpecies,
  DetectionSummary,
  AreaConcentration,
  SampleVolume,
  WaterPH,
  Temperature,
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

          {/* Area Concentration - 1x1 */}
          <div className="col-span-1 row-span-1">
            <AreaConcentration />
          </div>

          {/* Sample Volume - 1x1 */}
          <div className="col-span-1 row-span-1">
            <SampleVolume />
          </div>

          {/* Water pH - 1x1 */}
          <div className="col-span-1 row-span-1">
            <WaterPH />
          </div>

          {/* Temperature - 2x1 */}
          <div className="col-span-2 row-span-1">
            <Temperature />
          </div>

          {/* Additional metrics to fill space */}
          <div className="col-span-1 row-span-1">
            <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3">
              <div className="text-xs font-medium text-[var(--foreground)] mb-1">Turbidity</div>
              <div className="text-xs text-[var(--muted)] mb-2">NTU</div>
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--foreground)]">3.1</div>
                  <div className="w-8 h-8 bg-gradient-to-br from-green-100 to-teal-100 rounded-full flex items-center justify-center mx-auto mt-2">
                    <div className="w-4 h-4 bg-green-400 rounded-full opacity-60" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Dissolved Oxygen */}
          <div className="col-span-1 row-span-1">
            <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3">
              <div className="text-xs font-medium text-[var(--foreground)] mb-1">Dissolved O₂</div>
              <div className="text-xs text-[var(--muted)] mb-2">mg/L</div>
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--foreground)]">8.5</div>
                  <div className="w-8 h-8 bg-gradient-to-br from-sky-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mt-2">
                    <div className="w-4 h-4 bg-sky-400 rounded-full opacity-60" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Salinity */}
          <div className="col-span-1 row-span-1">
            <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3">
              <div className="text-xs font-medium text-[var(--foreground)] mb-1">Salinity</div>
              <div className="text-xs text-[var(--muted)] mb-2">PSU</div>
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-lg font-bold text-[var(--foreground)]">35.2</div>
                  <div className="w-8 h-8 bg-gradient-to-br from-violet-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mt-2">
                    <div className="w-4 h-4 bg-violet-400 rounded-full opacity-60" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Analysis Status */}
          <div className="col-span-1 row-span-1">
            <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3">
              <div className="text-xs font-medium text-[var(--foreground)] mb-1">Status</div>
              <div className="text-xs text-[var(--muted)] mb-2">Analysis</div>
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full mb-2">
                    Active
                  </div>
                  <div className="w-8 h-8 bg-gradient-to-br from-emerald-100 to-green-100 rounded-full flex items-center justify-center mx-auto">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}