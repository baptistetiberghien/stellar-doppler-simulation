<script setup lang="ts">
import { computed } from "vue";
import type { MultiSpotParams, MultiSpotResult, SpotInfo } from "../types/simulation";

const props = defineProps<{
  params: MultiSpotParams;
  result: MultiSpotResult | null;
}>();

const W = 300;
const H = 300;
const CX = W / 2;
const CY = H / 2;
const R = 120;

const incRad = computed(() => (props.params.inclination_deg * Math.PI) / 180);

function projectPoint(xs: number, ys: number, zs: number, inc: number) {
  return {
    x: xs,
    y: ys * Math.sin(inc) - zs * Math.cos(inc),
    z: ys * Math.cos(inc) + zs * Math.sin(inc),
  };
}

function spotToPath(spot: SpotInfo, inc: number): string | null {
  if (!spot.visible) return null;

  const lonR = (spot.lon_deg * Math.PI) / 180;
  const latR = (spot.lat_deg * Math.PI) / 180;
  const angR = Math.asin(Math.min(spot.radius, 1.0));

  const cx = Math.cos(latR) * Math.sin(lonR);
  const cy = Math.sin(latR);
  const cz = Math.cos(latR) * Math.cos(lonR);

  let tx: number, ty: number, tz: number;
  if (Math.abs(cy) < 0.9) {
    tx = cz; ty = 0; tz = -cx;
  } else {
    tx = 0; ty = cz; tz = -cy;
  }
  const tLen = Math.sqrt(tx * tx + ty * ty + tz * tz);
  if (tLen < 1e-10) return null;
  tx /= tLen; ty /= tLen; tz /= tLen;
  const ux = cy * tz - cz * ty;
  const uy = cz * tx - cx * tz;
  const uz = cx * ty - cy * tx;

  const cosA = Math.cos(angR);
  const sinA = Math.sin(angR);
  const pts: { sx: number; sy: number }[] = [];
  const N = 36;

  for (let i = 0; i < N; i++) {
    const phi = (2 * Math.PI * i) / N;
    const bx = cx * cosA + (tx * Math.cos(phi) + ux * Math.sin(phi)) * sinA;
    const by = cy * cosA + (ty * Math.cos(phi) + uy * Math.sin(phi)) * sinA;
    const bz = cz * cosA + (tz * Math.cos(phi) + uz * Math.sin(phi)) * sinA;
    const p = projectPoint(bx, by, bz, inc);
    if (p.z <= 0) continue;
    pts.push({ sx: CX + p.x * R, sy: CY - p.y * R });
  }
  if (pts.length < 3) return null;
  return "M " + pts.map(p => `${p.sx.toFixed(1)} ${p.sy.toFixed(1)}`).join(" L ") + " Z";
}

const spotPaths = computed(() => {
  if (!props.result) return [];
  return props.result.spots
    .map(s => spotToPath(s, incRad.value))
    .filter((p): p is string => p !== null);
});

const axisProjLen = computed(() => R * Math.sin(incRad.value));
const axisExtend = 1.15;
const showAxis = computed(() => props.params.inclination_deg > 3);
</script>

<template>
  <svg :width="W" :height="H" :viewBox="`0 0 ${W} ${H}`" class="star-view">
    <defs>
      <linearGradient id="dopplerGradMS" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#4488ff" stop-opacity="0.30" />
        <stop offset="50%" stop-color="#ffffff" stop-opacity="0" />
        <stop offset="100%" stop-color="#ff4444" stop-opacity="0.30" />
      </linearGradient>
      <radialGradient id="limbGradMS" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#fff8e0" />
        <stop offset="55%" stop-color="#ffe066" />
        <stop offset="100%" stop-color="#c68a00" />
      </radialGradient>
      <clipPath id="diskClipMS">
        <circle :cx="CX" :cy="CY" :r="R" />
      </clipPath>
    </defs>

    <circle :cx="CX" :cy="CY" :r="R" fill="url(#limbGradMS)" />
    <circle :cx="CX" :cy="CY" :r="R" fill="url(#dopplerGradMS)" />

    <!-- Rotation axis -->
    <line v-if="showAxis"
      :x1="CX" :y1="CY - axisProjLen * axisExtend"
      :x2="CX" :y2="CY + axisProjLen * axisExtend"
      stroke="#ffffffbb" stroke-width="1.5" stroke-dasharray="5,4" />

    <!-- All spots -->
    <path v-for="(d, i) in spotPaths" :key="i"
      :d="d"
      clip-path="url(#diskClipMS)"
      fill="#222" fill-opacity="0.82" stroke="#111" stroke-width="0.6" />

    <!-- Labels -->
    <text :x="CX - R - 5" :y="CY + 4" text-anchor="end" class="label-blue">← blue</text>
    <text :x="CX + R + 5" :y="CY + 4" text-anchor="start" class="label-red">red →</text>
    <text v-if="result" :x="CX" :y="H - 6" text-anchor="middle" class="label-count">
      {{ result.spots.filter(s => s.visible).length }}/{{ result.spots.length }} spots visible
    </text>
  </svg>
</template>

<style scoped>
.star-view { display: block; margin: 0 auto; max-width: 100%; height: auto; }
.label-blue { font: 10px sans-serif; fill: #5599ff; }
.label-red  { font: 10px sans-serif; fill: #ff6666; }
.label-count { font: 11px monospace; fill: #888; }
</style>
