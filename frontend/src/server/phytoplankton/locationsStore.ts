export type Marker = { id: string; coords: [number, number] };

// In-memory species -> markers map
const store = new Map<string, Marker[]>();

function norm(name: string) {
  return name.trim().toLowerCase();
}

export function setSpeciesMarkers(species: string, markers: Marker[]) {
  store.set(norm(species), markers);
}

export function addSpeciesMarkers(species: string, markers: Marker[]) {
  const key = norm(species);
  const prev = store.get(key) ?? [];
  const merged = [...prev, ...markers];
  store.set(key, merged);
}

export function getSpeciesMarkers(species: string): Marker[] {
  return store.get(norm(species)) ?? [];
}

export function getAllSpecies(): string[] {
  return Array.from(store.keys());
}

export function clearAll() {
  store.clear();
}
