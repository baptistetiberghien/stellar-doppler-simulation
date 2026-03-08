<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from "vue";
import type { SimulationResult } from "../types/simulation";

const props = defineProps<{
  result: SimulationResult | null;
}>();

const container = ref<HTMLDivElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const width = ref(600);
const height = ref(400);

const PADDING = { top: 24, right: 16, bottom: 40, left: 54 };

function drawPlot() {
  const ctx = canvas.value?.getContext("2d");
  if (!ctx || !props.result) return;

  const { wavelength, flux } = props.result;
  const n = wavelength.length;
  if (n < 2) return;

  const W = width.value;
  const H = height.value;
  const dpr = window.devicePixelRatio || 1;
  canvas.value!.width = W * dpr;
  canvas.value!.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  ctx.clearRect(0, 0, W, H);

  const plotW = W - PADDING.left - PADDING.right;
  const plotH = H - PADDING.top - PADDING.bottom;

  const xMin = wavelength[0];
  const xMax = wavelength[n - 1];
  const yMin = Math.min(...flux) - 0.01;
  const yMax = 1.005;

  function toX(v: number) { return PADDING.left + ((v - xMin) / (xMax - xMin)) * plotW; }
  function toY(v: number) { return PADDING.top + (1 - (v - yMin) / (yMax - yMin)) * plotH; }

  // Grid
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 0.5;
  const nTicksY = 5;
  for (let i = 0; i <= nTicksY; i++) {
    const v = yMin + (i / nTicksY) * (yMax - yMin);
    const py = toY(v);
    ctx.beginPath(); ctx.moveTo(PADDING.left, py); ctx.lineTo(W - PADDING.right, py); ctx.stroke();
  }
  const nTicksX = 6;
  for (let i = 0; i <= nTicksX; i++) {
    const v = xMin + (i / nTicksX) * (xMax - xMin);
    const px = toX(v);
    ctx.beginPath(); ctx.moveTo(px, PADDING.top); ctx.lineTo(px, PADDING.top + plotH); ctx.stroke();
  }

  // Axes labels
  ctx.fillStyle = "#bbb";
  ctx.font = "12px monospace";
  ctx.textAlign = "center";
  for (let i = 0; i <= nTicksX; i++) {
    const v = xMin + (i / nTicksX) * (xMax - xMin);
    ctx.fillText(v.toFixed(2), toX(v), PADDING.top + plotH + 18);
  }
  ctx.textAlign = "right";
  for (let i = 0; i <= nTicksY; i++) {
    const v = yMin + (i / nTicksY) * (yMax - yMin);
    ctx.fillText(v.toFixed(3), PADDING.left - 6, toY(v) + 4);
  }

  // Axis titles
  ctx.fillStyle = "#999";
  ctx.font = "13px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Wavelength (nm)", PADDING.left + plotW / 2, H - 4);
  ctx.save();
  ctx.translate(14, PADDING.top + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Normalised flux", 0, 0);
  ctx.restore();

  // Spectrum line
  ctx.beginPath();
  ctx.moveTo(toX(wavelength[0]), toY(flux[0]));
  for (let i = 1; i < n; i++) {
    ctx.lineTo(toX(wavelength[i]), toY(flux[i]));
  }
  ctx.strokeStyle = "#42b883";
  ctx.lineWidth = 2;
  ctx.stroke();
}

const resizeObserver = new ResizeObserver(() => {
  if (container.value) {
    width.value = container.value.clientWidth;
    height.value = container.value.clientHeight;
  }
});

onMounted(() => {
  if (container.value) {
    resizeObserver.observe(container.value);
    width.value = container.value.clientWidth;
    height.value = container.value.clientHeight;
  }
});

onUnmounted(() => resizeObserver.disconnect());

watch([() => props.result, width, height], drawPlot, { deep: true, flush: "post" });
</script>

<template>
  <div ref="container" class="spectrum-container">
    <canvas ref="canvas" :style="{ width: width + 'px', height: height + 'px' }" />
    <div v-if="!result" class="placeholder">Waiting for simulation data…</div>
  </div>
</template>

<style scoped>
.spectrum-container {
  width: 100%;
  flex: 1;
  min-height: 0;
  position: relative;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}
canvas {
  display: block;
}
.placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
}
</style>
