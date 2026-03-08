<script setup lang="ts">
import { computed } from "vue";
import type { SimulationParams, SimulationResult } from "../types/simulation";

const props = defineProps<{
  params: SimulationParams;
  result: SimulationResult | null;
}>();

const SIZE = 260;
const CX = SIZE / 2;
const CY = SIZE / 2;
const R = SIZE / 2 - 14;

// Client-side spot projection (same maths as backend activity.py)
// so the spot moves at 60fps without waiting for the API response.
const spotLocal = computed(() => {
  const lonRad = (props.params.spot_lon_deg * Math.PI) / 180;
  const latRad = (props.params.spot_lat_deg * Math.PI) / 180;
  const incRad = (props.params.inclination_deg * Math.PI) / 180;

  const xs = Math.cos(latRad) * Math.sin(lonRad);
  const ys = Math.sin(latRad);
  const zs = Math.cos(latRad) * Math.cos(lonRad);

  const xProj = xs;
  const yProj = ys * Math.cos(incRad) - zs * Math.sin(incRad);
  const zProj = ys * Math.sin(incRad) + zs * Math.cos(incRad);

  if (zProj <= 0) return null;

  return {
    cx: CX + xProj * R,
    cy: CY - yProj * R,
    r: props.params.spot_radius * R,
  };
});

const incRad = computed(() => (props.params.inclination_deg * Math.PI) / 180);

const axisTop = computed(() => ({
  x: CX,
  y: CY - R * Math.cos(incRad.value) * 1.15,
}));

const axisBot = computed(() => ({
  x: CX,
  y: CY + R * Math.cos(incRad.value) * 1.15,
}));
</script>

<template>
  <svg :width="SIZE" :height="SIZE" :viewBox="`0 0 ${SIZE} ${SIZE}`" class="star-view">
    <defs>
      <linearGradient id="dopplerGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#4488ff" stop-opacity="0.35" />
        <stop offset="50%" stop-color="#ffffff" stop-opacity="0" />
        <stop offset="100%" stop-color="#ff4444" stop-opacity="0.35" />
      </linearGradient>
      <radialGradient id="limbGrad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#fff8e0" />
        <stop offset="60%" stop-color="#ffe066" />
        <stop offset="100%" stop-color="#c68a00" />
      </radialGradient>
    </defs>

    <!-- Stellar disk -->
    <circle :cx="CX" :cy="CY" :r="R" fill="url(#limbGrad)" />
    <circle :cx="CX" :cy="CY" :r="R" fill="url(#dopplerGrad)" />

    <!-- Rotation axis -->
    <line
      :x1="axisTop.x" :y1="axisTop.y"
      :x2="axisBot.x" :y2="axisBot.y"
      stroke="#ffffff88" stroke-width="1.5" stroke-dasharray="5,4"
    />

    <!-- Spot (computed locally — instant response) -->
    <circle
      v-if="spotLocal"
      :cx="spotLocal.cx" :cy="spotLocal.cy" :r="spotLocal.r"
      fill="#222" fill-opacity="0.85" stroke="#111" stroke-width="1"
    />
  </svg>
</template>

<style scoped>
.star-view {
  display: block;
  margin: 0 auto;
  max-width: 100%;
  height: auto;
}
</style>
