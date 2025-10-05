"use client";
import { useEffect, useRef, useState } from 'react';

export interface EmulationMetricEvent {
  timestamp: string;
  species: string;
  raw: number;
  movingAvg: number | null;
  baseline: number | null;
  threshold: number | null;
  breach: boolean;
  alertTriggered: boolean;
  spikeActive: boolean;
  metrics: {
    ph: number;
    temperature: number;
    dissolvedOxygen: number;
    areaContribution: number;
    sampleVolumeMl: number;
  };
}

interface StateShape {
  running: boolean;
  species: Record<string, EmulationMetricEvent[]>;
  latestAggregates: {
    ph?: number;
    temperature?: number;
    dissolvedOxygen?: number;
    totalArea?: number;
    totalVolume?: number;
  };
}

export function useEmulationStream() {
  const [state, setState] = useState<StateShape>({ running: false, species: {}, latestAggregates: {} });
  const totalsRef = useRef<{ ph: number[]; temp: number[]; do: number[]; area: number; volume: number }>({ ph: [], temp: [], do: [], area: 0, volume: 0 });

  useEffect(() => {
    const es = new EventSource('http://localhost:5001/emulate/stream');

    es.onmessage = (e) => {
      if (!e.data) return;
      try {
        const payload = JSON.parse(e.data);
        if (payload.type === 'emulation_status') {
          setState(s => ({ ...s, running: payload.running }));
          return;
        }
        if (payload.type === 'emulation_tick') {
          // Defensive: ensure metrics object always exists
          if (!payload.metrics) {
            payload.metrics = {
              ph: 0,
              temperature: 0,
              dissolvedOxygen: 0,
              areaContribution: 0,
              sampleVolumeMl: 0
            };
          }
          const evt: EmulationMetricEvent = payload as EmulationMetricEvent;
          setState(prev => {
            const cloneSpecies = { ...prev.species };
            const list = cloneSpecies[evt.species] ? [...cloneSpecies[evt.species]] : [];
            list.push(evt);
            if (list.length > 300) list.shift();
            cloneSpecies[evt.species] = list;

            // Aggregates
            totalsRef.current.ph.push(evt.metrics.ph);
            if (totalsRef.current.ph.length > 50) totalsRef.current.ph.shift();
            totalsRef.current.temp.push(evt.metrics.temperature);
            if (totalsRef.current.temp.length > 50) totalsRef.current.temp.shift();
            totalsRef.current.do.push(evt.metrics.dissolvedOxygen);
            if (totalsRef.current.do.length > 50) totalsRef.current.do.shift();
            totalsRef.current.area += evt.metrics.areaContribution;
            totalsRef.current.volume += evt.metrics.sampleVolumeMl;

            const avg = (arr: number[]) => arr.reduce((a,b)=>a+b,0)/Math.max(1,arr.length);
            return {
              running: true,
              species: cloneSpecies,
              latestAggregates: {
                ph: avg(totalsRef.current.ph),
                temperature: avg(totalsRef.current.temp),
                dissolvedOxygen: avg(totalsRef.current.do),
                totalArea: totalsRef.current.area,
                totalVolume: totalsRef.current.volume,
              }
            };
          });
        }
        if (payload.type === 'emulation_complete') {
          setState(s => ({ ...s, running: false }));
        }
      } catch {}
    };

    return () => { es.close(); };
  }, []);

  return state;
}
