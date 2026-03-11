<script setup lang="ts">
import { computed } from "vue";
import type { SimulationParams, SimulationResult } from "../types/simulation";

const props = defineProps<{
  params: SimulationParams;
  result: SimulationResult | null;
}>();

// ── Main disk layout ──
const W = 300;
const H = 420;
const CX = W / 2;
const CY = 150;
const R = 105;

const incRad = computed(() => (props.params.inclination_deg * Math.PI) / 180);

// ── Spot projection (spherical cap → projected polygon) ──

function projectPoint(xs: number, ys: number, zs: number, inc: number) {
  const xP = xs;
  const yP = ys * Math.sin(inc) - zs * Math.cos(inc);
  const zP = ys * Math.cos(inc) + zs * Math.sin(inc);
  return { x: xP, y: yP, z: zP };
}

const spotPath = computed(() => {
  const lon = (props.params.spot_lon_deg * Math.PI) / 180;
  const lat = (props.params.spot_lat_deg * Math.PI) / 180;
  const inc = incRad.value;
  const angRadius = Math.asin(Math.min(props.params.spot_radius, 1.0));

  // Spot center on unit sphere (stellar frame)
  const cx = Math.cos(lat) * Math.sin(lon);
  const cy = Math.sin(lat);
  const cz = Math.cos(lat) * Math.cos(lon);

  // Build two tangent vectors orthogonal to (cx, cy, cz)
  let tx: number, ty: number, tz: number;
  if (Math.abs(cy) < 0.9) {
    // cross(c, ŷ)
    tx = cz; ty = 0; tz = -cx;
  } else {
    // cross(c, x̂)
    tx = 0; ty = cz; tz = -cy;
  }
  const tLen = Math.sqrt(tx * tx + ty * ty + tz * tz);
  tx /= tLen; ty /= tLen; tz /= tLen;
  // Second tangent: cross(c, t1)
  const ux = cy * tz - cz * ty;
  const uy = cz * tx - cx * tz;
  const uz = cx * ty - cy * tx;

  // Sample boundary of the spherical cap
  const N = 48;
  const cosA = Math.cos(angRadius);
  const sinA = Math.sin(angRadius);
  const pts: { sx: number; sy: number }[] = [];

  for (let i = 0; i < N; i++) {
    const phi = (2 * Math.PI * i) / N;
    const cosPhi = Math.cos(phi);
    const sinPhi = Math.sin(phi);

    // Point on sphere at angular distance angRadius from center
    const bx = cx * cosA + (tx * cosPhi + ux * sinPhi) * sinA;
    const by = cy * cosA + (ty * cosPhi + uy * sinPhi) * sinA;
    const bz = cz * cosA + (tz * cosPhi + uz * sinPhi) * sinA;

    const p = projectPoint(bx, by, bz, inc);
    if (p.z <= 0) continue;
    pts.push({ sx: CX + p.x * R, sy: CY - p.y * R });
  }

  if (pts.length < 3) return null;
  return "M " + pts.map((p) => `${p.sx.toFixed(1)} ${p.sy.toFixed(1)}`).join(" L ") + " Z";
});

// ── Projected rotation axis ──
const axisProjLen = computed(() => R * Math.sin(incRad.value));
const axisExtend = 1.18;
const axisTop = computed(() => ({
  x: CX,
  y: CY - axisProjLen.value * axisExtend,
}));
const axisBot = computed(() => ({
  x: CX,
  y: CY + axisProjLen.value * axisExtend,
}));
const showAxis = computed(() => props.params.inclination_deg > 3);

// ── Rotation direction arrow ──
const rotR = R + 12;
const rotArc = computed(() => {
  const a1 = Math.PI * 0.7;
  const a2 = Math.PI * 0.3;
  const s = { x: CX + rotR * Math.cos(a1), y: CY + rotR * Math.sin(a1) };
  const e = { x: CX + rotR * Math.cos(a2), y: CY + rotR * Math.sin(a2) };
  return `M ${s.x} ${s.y} A ${rotR} ${rotR} 0 0 0 ${e.x} ${e.y}`;
});

// ── Side-view schematic ──
const svCX = W / 2;
const svCY = 335;
const svR = 28;
const svArrowLen = 55;

const svAxisTip = computed(() => ({
  x: svCX + svR * 1.6 * Math.sin(incRad.value),
  y: svCY - svR * 1.6 * Math.cos(incRad.value),
}));
const svIncArc = computed(() => {
  const r = 20;
  const a = incRad.value;
  if (a < 0.05) return null;
  const x1 = svCX;
  const y1 = svCY - r;
  const x2 = svCX + r * Math.sin(a);
  const y2 = svCY - r * Math.cos(a);
  return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`;
});
const svIncLabel = computed(() => {
  const r = 28;
  const a = incRad.value / 2;
  return {
    x: svCX + r * Math.sin(a) + 4,
    y: svCY - r * Math.cos(a) + 4,
  };
});
</script>

<template>
  <svg :width="W" :height="H" :viewBox="`0 0 ${W} ${H}`" class="star-view">
    <defs>
      <linearGradient id="dopplerGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#4488ff" stop-opacity="0.30" />
        <stop offset="50%" stop-color="#ffffff" stop-opacity="0" />
        <stop offset="100%" stop-color="#ff4444" stop-opacity="0.30" />
      </linearGradient>
      <radialGradient id="limbGrad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#fff8e0" />
        <stop offset="55%" stop-color="#ffe066" />
        <stop offset="100%" stop-color="#c68a00" />
      </radialGradient>
      <!-- Clip to stellar disk so the spot never bleeds outside -->
      <clipPath id="diskClip">
        <circle :cx="CX" :cy="CY" :r="R" />
      </clipPath>
      <marker id="arrRot" markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto">
        <polygon points="0 0, 7 2.5, 0 5" fill="#aaa" />
      </marker>
      <marker id="arrAxis" markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto">
        <polygon points="0 0.5, 6 2.5, 0 4.5" fill="#ccc" />
      </marker>
    </defs>

    <!-- ════════════ MAIN STAR DISK ════════════ -->
    <circle :cx="CX" :cy="CY" :r="R" fill="url(#limbGrad)" />
    <circle :cx="CX" :cy="CY" :r="R" fill="url(#dopplerGrad)" />

    <!-- Rotation axis -->
    <line v-if="showAxis"
      :x1="axisTop.x" :y1="axisTop.y"
      :x2="axisBot.x" :y2="axisBot.y"
      stroke="#ffffffbb" stroke-width="1.5" stroke-dasharray="5,4"
    />
    <text v-if="showAxis" :x="axisTop.x + 10" :y="axisTop.y - 2"
      text-anchor="start" class="label-pole">N</text>
    <text v-if="showAxis" :x="axisBot.x + 10" :y="axisBot.y + 4"
      text-anchor="start" class="label-pole">S</text>

    <!-- Rotation arrow Ω -->
    <path :d="rotArc" fill="none" stroke="#aaa" stroke-width="1" marker-end="url(#arrRot)" opacity="0.55" />
    <text :x="CX + R + 4" :y="CY - R - 10" text-anchor="start" class="label-omega">Ω</text>

    <!-- Doppler labels -->
    <text :x="CX - R - 6" :y="CY + 4" text-anchor="end" class="label-blue">← blue</text>
    <text :x="CX + R + 6" :y="CY + 4" text-anchor="start" class="label-red">red →</text>

    <!-- Spot (projected spherical cap, clipped to disk) -->
    <path v-if="spotPath"
      :d="spotPath"
      clip-path="url(#diskClip)"
      fill="#222" fill-opacity="0.85" stroke="#111" stroke-width="0.8"
    />

    <!-- ════════════ SEPARATOR ════════════ -->
    <line :x1="20" :y1="280" :x2="W - 20" :y2="280"
      stroke="#333" stroke-width="0.5" />
    <text :x="W / 2" :y="295" text-anchor="middle" class="label-section">
      Side view (geometry)
    </text>

    <!-- ════════════ SIDE-VIEW SCHEMATIC ════════════ -->
    <circle :cx="svCX" :cy="svCY" :r="svR"
      fill="none" stroke="#ffe066" stroke-width="1.5" opacity="0.6" />

    <line :x1="svCX" :y1="svCY + svArrowLen" :x2="svCX" :y2="svCY + svR + 4"
      stroke="#6ea8fe" stroke-width="1.5" marker-end="url(#arrAxis)" />
    <text :x="svCX + 2" :y="svCY + svArrowLen + 14" text-anchor="middle" class="label-observer">
      Observer
    </text>
    <text :x="svCX - 14" :y="svCY + svArrowLen - 10" text-anchor="end" class="label-los">LOS</text>

    <line :x1="svCX" :y1="svCY"
      :x2="svAxisTip.x" :y2="svAxisTip.y"
      stroke="#ffffffbb" stroke-width="1.5" stroke-dasharray="4,3" />
    <text :x="svAxisTip.x + 8" :y="svAxisTip.y - 2" text-anchor="start" class="label-pole-sm">N</text>

    <path v-if="svIncArc" :d="svIncArc"
      fill="none" stroke="#6ea8fe" stroke-width="1.2" opacity="0.8" />
    <text v-if="params.inclination_deg > 3"
      :x="svIncLabel.x" :y="svIncLabel.y"
      text-anchor="start" class="label-inc">
      i={{ Math.round(params.inclination_deg) }}°
    </text>
    <text v-if="params.inclination_deg <= 3"
      :x="svCX + 30" :y="svCY - 20"
      text-anchor="start" class="label-inc">
      i≈0° (pole-on)
    </text>
  </svg>
</template>

<style scoped>
.star-view {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}
.label-pole     { font: bold 11px sans-serif; fill: #ccc; }
.label-pole-sm  { font: bold 10px sans-serif; fill: #ccc; }
.label-omega    { font: bold 14px serif; fill: #aaa; }
.label-blue     { font: 10px sans-serif; fill: #5599ff; }
.label-red      { font: 10px sans-serif; fill: #ff6666; }
.label-section  { font: italic 10px sans-serif; fill: #666; }
.label-observer { font: 11px sans-serif; fill: #6ea8fe; }
.label-los      { font: 10px sans-serif; fill: #6ea8fe; opacity: 0.7; }
.label-inc      { font: 11px monospace; fill: #6ea8fe; }
</style>
