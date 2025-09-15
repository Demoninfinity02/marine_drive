"use client";

export default function DetectionSummary() {
  const detections = [
    { species: "Copepod", genus: "Acartia", count: "2,341", size: "2.1", confidence: 95 },
    { species: "Alexandrium", genus: "Alexandrium", count: "1,859", size: "1.8", confidence: 92 },
    { species: "Diatoms", genus: "Thalassiosira", count: "1,623", size: "3.2", confidence: 88 },
    { species: "Ceratium", genus: "Ceratium", count: "1,234", size: "4.1", confidence: 91 },
    { species: "Dinoflagellate", genus: "Prorocentrum", count: "987", size: "2.7", confidence: 85 },
    { species: "Protozoa", genus: "Paramecium", count: "743", size: "1.5", confidence: 89 },
    { species: "Gymnodinium", genus: "Gymnodinium", count: "654", size: "2.9", confidence: 87 },
    { species: "Rhizosolenia", genus: "Rhizosolenia", count: "432", size: "5.3", confidence: 93 },
  ];

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="p-3 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-[var(--foreground)]">
              Detection Summary
            </h3>
            <p className="text-xs text-[var(--muted)]">
              Species identification results
            </p>
          </div>
          <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">
            Active
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-3 overflow-y-auto">
        {/* Table Header */}
        <div className="grid grid-cols-5 gap-3 pb-2 border-b border-[var(--border)] text-xs font-medium text-[var(--muted)] mb-2">
          <div>Species</div>
          <div>Genus</div>
          <div>Count</div>
          <div>Size (μm)</div>
          <div>Confidence</div>
        </div>

        {/* Table Rows - compact spacing */}
        <div className="space-y-1">
          {detections.map((item, index) => (
            <div key={index} className="grid grid-cols-5 gap-3 py-2 px-2 rounded-md hover:bg-slate-50 transition-colors text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-gradient-to-br from-teal-100 to-emerald-100 rounded-sm flex items-center justify-center">
                  <div className="w-2 h-2 bg-teal-500 rounded-full opacity-60" />
                </div>
                <span className="font-medium text-[var(--foreground)] truncate">{item.species}</span>
              </div>
              <div className="text-[var(--muted)] truncate">{item.genus}</div>
              <div className="font-medium text-[var(--foreground)]">{item.count}</div>
              <div className="text-[var(--muted)]">{item.size}</div>
              <div className="flex items-center">
                <div className={`px-2 py-1 rounded-md text-xs font-medium ${
                  item.confidence >= 90 ? 'bg-emerald-100 text-emerald-700' :
                  item.confidence >= 85 ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {item.confidence}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}