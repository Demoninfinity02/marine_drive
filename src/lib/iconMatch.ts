export function normalize(s: string) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "");
}

export function bestMatchIcon(name: string, icons: string[]) {
  const n = normalize(name);

  // Prefer exact filename match, then genus prefix, then substring, then token overlap.
  function scoreFor(base: string) {
    if (!base) return 0;
    if (base === n) return 10_000 + base.length; // exact match wins
    if (base.startsWith(n + "-")) return 9_000 + n.length; // base is a specific variant of the genus
    if (n.startsWith(base + "-")) return 8_000 + base.length; // name is variant of base
    if (n.includes(base)) return 5_000 + base.length; // base is substring of name
    if (base.includes(n)) return 4_000 + n.length; // name is substring of base
    const nt = n.split("-");
    const bt = base.split("-");
    const overlap = nt.filter((t) => bt.includes(t));
    return overlap.join("-").length; // small score for any token overlap
  }

  let best: { file: string; score: number; len: number } | null = null;
  for (const file of icons) {
    const base = normalize(file.replace(/\.svg$/i, ""));
    const score = scoreFor(base);
    const len = base.length;
    if (!best || score > best.score || (score === best.score && len < best.len)) {
      best = { file, score, len };
    }
  }
  return best && best.score > 0 ? best.file : null;
}
