"use client";
import React, { useEffect, useRef, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface EmulationPoint {
  timestamp: string;
  species: string;
  raw: number;
  movingAvg: number | null;
  baseline: number | null;
  threshold: number | null;
  breach: boolean;
  alertTriggered: boolean;
}

const COLORS = [
  '#2563eb', '#dc2626', '#16a34a', '#9333ea', '#ea580c', '#0891b2', '#4f46e5', '#d97706'
];

function pickColor(i: number) { return COLORS[i % COLORS.length]; }

const MAX_POINTS = 180; // 15 minutes at 5s interval = 180 points

const EmulationCharts: React.FC = () => {
  const [dataMap, setDataMap] = useState<Record<string, EmulationPoint[]>>({});
  const [connected, setConnected] = useState(false);
  const [running, setRunning] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource('http://localhost:5001/emulate/stream');
    eventSourceRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    es.onmessage = (ev) => {
      if (!ev.data) return;
      try {
        const payload = JSON.parse(ev.data);
        if (payload.type === 'emulation_status') {
          setRunning(payload.running);
          return;
        }
        if (payload.type === 'emulation_tick' || payload.type === 'emulation_tick_batch') {
          setRunning(true);
          const records = payload.type === 'emulation_tick_batch' ? payload.records : [payload];
          setDataMap(prev => {
            const clone = { ...prev };
            records.forEach((r: any) => {
              const list = clone[r.species] ? [...clone[r.species]] : [];
              list.push(r);
              if (list.length > MAX_POINTS) list.shift();
              clone[r.species] = list;
            });
            return clone;
          });
        }
        if (payload.type === 'emulation_complete') {
          setRunning(false);
        }
      } catch (e) {
        // ignore parse errors
      }
    };

    return () => { es.close(); };
  }, []);

  const allTimestamps = Array.from(new Set(Object.values(dataMap).flat().map(p => p.timestamp))).sort();

  // Build datasets per species (raw + moving avg + threshold single line)
  const datasets: any[] = [];
  const speciesNames = Object.keys(dataMap).sort();
  speciesNames.forEach((species, idx) => {
    const series = dataMap[species];
    const color = pickColor(idx);
    const tsIndex: Record<string, EmulationPoint> = {};
    series.forEach(p => { tsIndex[p.timestamp] = p; });

    datasets.push({
      label: species + ' raw',
      data: allTimestamps.map(t => tsIndex[t]?.raw ?? null),
      borderColor: color,
      backgroundColor: color,
      pointRadius: 1,
      tension: 0.2,
    });
    datasets.push({
      label: species + ' m.avg',
      data: allTimestamps.map(t => tsIndex[t]?.movingAvg ?? null),
      borderColor: color,
      borderDash: [4,2],
      pointRadius: 0,
      tension: 0.2,
    });
    // Threshold (single value that may appear after baseline ready)
    datasets.push({
      label: species + ' threshold',
      data: allTimestamps.map(t => tsIndex[t]?.threshold ?? null),
      borderColor: color,
      borderDash: [2,6],
      pointRadius: 0,
      tension: 0,
    });
  });

  const chartData = {
    labels: allTimestamps.map(t => new Date(t).toLocaleTimeString([], {minute: '2-digit', second: '2-digit'})),
    datasets
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'nearest', intersect: false },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10 } },
      tooltip: {
        callbacks: {
          footer: (items: any) => {
            if (!items.length) return '';
            const i = items[0].dataIndex;
            const ts = allTimestamps[i];
            const lines: string[] = [];
            speciesNames.forEach(s => {
              const pt = dataMap[s].find(p => p.timestamp === ts);
              if (pt) {
                if (pt.alertTriggered) lines.push(`ALERT ${s}!`);
                else if (pt.breach) lines.push(`Breach ${s}`);
              }
            });
            return lines.join('\n');
          }
        }
      }
    },
    scales: {
      x: { ticks: { maxRotation: 0, autoSkip: true } },
      y: { beginAtZero: true }
    }
  };

  async function startEmulation() {
    await fetch('http://localhost:5001/emulate/start', { method: 'POST' });
  }

  return (
    <div className="h-full bg-white rounded-xl border border-[var(--border)] shadow-sm p-3 flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-semibold">Time Series Emulation</h2>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] ${connected ? 'text-green-600' : 'text-red-500'}`}>{connected ? 'LIVE' : 'OFF'}</span>
          <button onClick={startEmulation} disabled={running} className="px-2 py-1 rounded bg-blue-600 text-white text-[10px] disabled:opacity-40">Start</button>
        </div>
      </div>
      <div className="text-[10px] text-[var(--muted)] mb-2">Raw, moving average & threshold lines per species. Alerts only after sustained breaches.</div>
      <div className="flex-1"><Line data={chartData} options={options} /></div>
    </div>
  );
};

export default EmulationCharts;
