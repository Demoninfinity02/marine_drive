export type RawPhyto = {
  phytoplanktonscientificName: string;
  "no of that pyhtoplankon": string | number;
};

// Start with no data to avoid placeholders; the live feed or POST will populate this.
let _data: RawPhyto[] = [];

export function getData() {
  return _data;
}

export function setData(arr: RawPhyto[]) {
  _data = arr;
}
